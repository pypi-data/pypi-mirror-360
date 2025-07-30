"""Module for the stereo router of the Mynd API."""

from pathlib import Path
from typing import TypeAlias

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select

import mynd.api.dependencies as dependencies
import mynd.models.schema as schemas
import mynd.models.record as records

from mynd.api.image_store import ImageStore
from mynd.api.settings import ApplicationSettings
from mynd.database import Engine, Session

from mynd.distributed.tasks import (
    StereoExportTask,
    export_stereo_rectified_images,
    export_stereo_range_maps,
    export_stereo_geometry,
    process_stereo_rectification,
)

from mynd.utils.containers import Pair
from mynd.utils.log import logger


router = APIRouter()


@router.post(
    "/stereo_rigs/rectify",
    tags=["stereo"],
)
async def rectify_stereo_rigs(
    settings: dependencies.ApplicationSettingsDep,
    engine: dependencies.EngineDep,
) -> list[str]:
    """Rectifies all stereo rigs in the database by computing the rectified
    sensors and pixel maps."""

    with Session(engine) as session:
        stereo_rigs: list[records.StereoRigRecord] = session.exec(
            select(records.StereoRigRecord)
        ).all()
        ids: list[int] = [stereo_rig.id for stereo_rig in stereo_rigs]

    results: list = list()
    for id in ids:
        result = process_stereo_rectification.delay(settings=settings, rig_id=id)
        results.append(result.id)

    return results


@router.post(
    "/stereo_rigs/{id}/rectify", tags=["stereo"], response_model=schemas.StereoRigSchema
)
async def rectify_stereo_rig(
    engine: dependencies.EngineDep,
    settings: dependencies.ApplicationSettingsDep,
    id: int,
) -> schemas.StereoRigSchema:
    """Rectifies a stereo rig by computing the rectified sensors and the pixel
    maps to transform images between the unrectified and rectified sensors."""

    with Session(engine) as session:
        stereo_rig: records.StereoRigRecord | None = session.get(
            records.StereoRigRecord, id
        )

        if stereo_rig is None:
            raise HTTPException(404, detail=f"stereo rig not found: {id}")

    result = process_stereo_rectification.delay(settings=settings, rig_id=id)
    return {"task_id": result.id}


class StereoExportData(BaseModel):
    """Class representing data for stereo export tasks."""

    chunk: schemas.ChunkSchema
    stereo_rig: schemas.StereoRigWithMapsSchema
    camera_pairs: list[schemas.StereoRigBase.CameraPair]
    matcher_file: Path


def prepare_stereo_export_data(
    settings: ApplicationSettings, session: dependencies.SessionDep, stereo_rig_id: int
) -> StereoExportData:
    """Prepares data for stereo export tasks by loading it from the database."""

    stereo_rig: records.StereoRigRecord | None = session.get(
        records.StereoRigRecord, stereo_rig_id
    )

    if not stereo_rig:
        raise HTTPException(404, detail=f"stereo rig not found: {stereo_rig_id}")
    if not stereo_rig.chunk:
        raise HTTPException(404, detail=f"stereo rig missing chunk: {stereo_rig_id}")
    if not stereo_rig.sensors_rectified or not stereo_rig.pixel_maps:
        raise HTTPException(404, detail=f"stereo rig is not rectified: {stereo_rig_id}")

    matcher_file: Path = settings.stereo.model_file
    if not matcher_file.exists():
        raise HTTPException(404, detail=f"file does not exist: {matcher_file}")

    # Convert records to schemas
    chunk_schema: schemas.ChunkSchema = schemas.ChunkSchema.model_validate(
        stereo_rig.chunk
    )
    stereo_rig_schema: schemas.StereoRigWithMapsSchema = (
        schemas.StereoRigWithMapsSchema.model_validate(stereo_rig)
    )

    # Convert camera pairs
    camera_pair_schemas: list[schemas.StereoRigBase.CameraPair] = [
        schemas.StereoRigBase.CameraPair.model_validate(camera_pair_record)
        for camera_pair_record in stereo_rig.chunk.stereo_camera_pairs
    ]

    filtered_camera_pair_schemas: list[schemas.StereoRigBase.CameraPair] = [
        camera_pair
        for camera_pair in camera_pair_schemas
        if camera_pair.master.sensor == stereo_rig_schema.sensors.master
        and camera_pair.slave.sensor == stereo_rig_schema.sensors.slave
    ]

    return StereoExportData(
        chunk=chunk_schema,
        stereo_rig=stereo_rig_schema,
        camera_pairs=filtered_camera_pair_schemas,
        matcher_file=matcher_file,
    )


@router.post(
    "/stereo_rigs/{id}/{file_group_name}/export-rectified-images", tags=["stereo"]
)
async def export_rectified_images(
    session: dependencies.SessionDep,
    settings: dependencies.ApplicationSettingsDep,
    image_store: dependencies.ImageStoreDep,
    id: int,
    file_group_name: str,
) -> dict:
    """Rectifies images with a given stereo rig and writes the range maps to file."""

    export_data: StereoExportData = prepare_stereo_export_data(settings, session, id)

    # Create directory
    directory: Path = (
        settings.directories.export
        / f"{export_data.chunk.label}_rectified_{file_group_name}"
    )
    directory.mkdir(parents=True, exist_ok=True)

    if not directory.exists():
        raise HTTPException(404, detail=f"directory does not exist: {directory}")

    file_group: ImageStore.FileGroup | None = image_store.get_group(file_group_name)
    image_file_pairs: list[ImageFilePair] = retrieve_camera_image_pairs(
        file_group,
        export_data.camera_pairs,
    )

    # Add statistics and data to return to client
    data: dict = {
        "stereo_rig": export_data.stereo_rig.id,
        "master_sensor": export_data.stereo_rig.sensors.master.id,
        "slave_sensor": export_data.stereo_rig.sensors.master.id,
        "camera_pair_count": len(export_data.camera_pairs),
        "image_pairs": len(image_file_pairs),
        "export_directory": str(directory),
    }

    # Generate the stereo range maps in the background
    result = export_stereo_rectified_images.delay(
        directory,
        export_data.stereo_rig,
        image_file_pairs,
    )

    data["task_id"] = result.id
    return data


@router.post(
    "/stereo_rigs/{id}/{file_group_name}/export-rectified-ranges",
    tags=["stereo"],
)
async def export_rectified_ranges(
    settings: dependencies.ApplicationSettingsDep,
    session: dependencies.SessionDep,
    image_store: dependencies.ImageStoreDep,
    id: int,
    file_group_name: str,
) -> dict:
    """Rectifies images with a given stereo rig and writes the range maps to file."""

    export_data: StereoExportData = prepare_stereo_export_data(settings, session, id)
    file_group: ImageStore.FileGroup | None = image_store.get_group(file_group_name)

    if not file_group:
        raise HTTPException(404, detail=f"file group does not exist: {file_group}")

    # Select image pairs based on camera labels
    image_file_pairs: list[ImageFilePair] = retrieve_camera_image_pairs(
        file_group,
        export_data.camera_pairs,
    )

    # Create export directories
    export_directories: StereoExportTask.Directories = StereoExportTask.Directories(
        images=settings.directories.export
        / f"{export_data.chunk.label}_rectified_{file_group}",
        ranges=settings.directories.export
        / f"{export_data.chunk.label}_rectified_ranges",
        normals=settings.directories.export
        / f"{export_data.chunk.label}_rectified_normals",
    )

    # Make directories
    export_directories.ranges.mkdir(parents=True, exist_ok=True)

    # Add statistics and data to return to client
    data: dict = {
        "stereo_rig": export_data.stereo_rig.id,
        "master_sensor": export_data.stereo_rig.sensors.master.id,
        "slave_sensor": export_data.stereo_rig.sensors.master.id,
        "camera_pair_count": len(export_data.camera_pairs),
        "image_pairs": len(image_file_pairs),
        "export_directories": export_directories.model_dump(),
    }

    # Generate and export the stereo range maps in the background
    result = export_stereo_range_maps.delay(
        export_directories,
        export_data.stereo_rig,
        image_file_pairs,
        export_data.matcher_file,
    )

    data["task_id"] = result.id
    return data


@router.post(
    "/stereo_rigs/{id}/{file_group_name}/export-rectified-geometry",
    tags=["stereo"],
)
async def export_rectified_geometry(
    settings: dependencies.ApplicationSettingsDep,
    session: dependencies.SessionDep,
    image_store: dependencies.ImageStoreDep,
    id: int,
    file_group_name: str,
) -> dict:
    """Computes a stereo geometry for a given rig and matcher, and export the
    ranges and normals."""

    export_data: StereoExportData = prepare_stereo_export_data(settings, session, id)
    file_group: ImageStore.FileGroup | None = image_store.get_group(file_group_name)

    if not file_group:
        raise HTTPException(404, detail=f"file group does not exist: {file_group}")

    # Select image pairs based on camera labels
    image_file_pairs: list[ImageFilePair] = retrieve_camera_image_pairs(
        file_group,
        export_data.camera_pairs,
    )

    # Create export directories
    export_directories: StereoExportTask.Directories = StereoExportTask.Directories(
        images=settings.directories.export
        / f"{export_data.chunk.label}_rectified_images",
        ranges=settings.directories.export
        / f"{export_data.chunk.label}_rectified_ranges",
        normals=settings.directories.export
        / f"{export_data.chunk.label}_rectified_normals",
    )

    # Make directories for ranges and normals
    export_directories.ranges.mkdir(parents=True, exist_ok=True)
    export_directories.normals.mkdir(parents=True, exist_ok=True)

    # Add statistics and data to return to client
    data: dict = {
        "stereo_rig": export_data.stereo_rig.id,
        "master_sensor": export_data.stereo_rig.sensors.master.id,
        "slave_sensor": export_data.stereo_rig.sensors.master.id,
        "camera_pair_count": len(export_data.camera_pairs),
        "image_pairs": len(image_file_pairs),
        "export_directories": export_directories.model_dump(),
    }

    # Generate and export the stereo geometry in the background
    result = export_stereo_geometry.delay(
        export_directories,
        export_data.stereo_rig,
        image_file_pairs,
        export_data.matcher_file,
    )

    data["task_id"] = result.id
    return data


ImageFilePair: TypeAlias = Pair[Path]


def retrieve_camera_image_pairs(
    file_group: ImageStore.FileGroup,
    camera_pairs: list[records.StereoRigRecord.CameraPair],
) -> list[ImageFilePair]:
    """Retrieves image files for a collection of stereo camera pairs."""

    image_file_pairs: list[ImageFilePair] = list()
    for camera_pair in camera_pairs:
        image_file_pair: ImageFilePair = Pair(
            first=file_group.retrieve_by_stem(camera_pair.master.image_label),
            second=file_group.retrieve_by_stem(camera_pair.slave.image_label),
        )

        if image_file_pair.first is None:
            logger.warning(f"missing image for camera: {camera_pair.master.label}")
            continue

        if image_file_pair.second is None:
            logger.warning(f"missing image for camera: {camera_pair.slave.label}")
            continue

        image_file_pairs.append(image_file_pair)

    return image_file_pairs
