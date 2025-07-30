"""Module for the stereo router of the Mynd API."""

from pathlib import Path
from typing import TypeAlias

from fastapi import APIRouter, HTTPException
from sqlmodel import select

import mynd.api.dependencies as deps
import mynd.models.schema as schemas
import mynd.models.record as records

from mynd.utils.containers import Pair
from mynd.utils.log import logger


router = APIRouter()


@router.get(
    "/stereo_rigs/chunk/{chunk_id}",
    tags=["stereo"],
    response_model=list[schemas.StereoRigSchema],
)
async def read_stereo_rigs_by_chunk(
    session: deps.SessionDep, chunk_id: int
) -> list[schemas.StereoRigSchema]:
    """Reads the stereo rigs in a chunk."""
    chunk_model: records.ChunkRecord | None = session.get(records.ChunkRecord, chunk_id)
    if not chunk_model:
        raise HTTPException(404, detail=f"chunk not found: {chunk_id}")
    return chunk_model.stereo_rigs


@router.get(
    "/stereo_rigs/all",
    tags=["stereo"],
    response_model=list[schemas.StereoRigSchema],
)
async def read_stereo_rigs_all(
    session: deps.SessionDep,
) -> list[schemas.StereoRigSchema]:
    """Reads all stereo rigs from the database."""
    stereo_rig_records: list[records.StereoRigRecord] = session.exec(
        select(records.StereoRigRecord)
    ).all()

    stereo_rigs_schemas: list[schemas.StereoRigSchema] = [
        schemas.StereoRigSchema.model_validate(record) for record in stereo_rig_records
    ]
    return stereo_rigs_schemas


@router.get(
    "/stereo_rigs/{id}",
    tags=["stereo"],
    response_model=schemas.StereoRigSchema,
)
async def read_stereo_rigs_by_id(
    session: deps.SessionDep, id: int
) -> schemas.StereoRigSchema:
    """Reads a stereo rig by the master and slave sensor ids."""
    stereo_rig_model: records.StereoRigRecord = session.get(records.StereoRigRecord, id)
    if not stereo_rig_model:
        raise HTTPException(404, detail=f"stereo rig not found: {id}")
    return stereo_rig_model


@router.get(
    "/stereo_sensor_pairs/chunk/{chunk_id}",
    tags=["stereo"],
    response_model=list[schemas.StereoRigSchema.SensorPair],
)
async def read_stereo_sensors_by_chunk(
    session: deps.SessionDep, chunk_id: int
) -> list[schemas.StereoRigSchema.SensorPair]:
    """Reads a stereo sensor pairs in a chunk."""
    chunk_model: records.ChunkRecord | None = session.get(records.ChunkRecord, chunk_id)
    if not chunk_model:
        raise HTTPException(404, detail=f"chunk not found: {chunk_id}")
    return chunk_model.stereo_sensor_pairs


@router.get(
    "/stereo_camera_pairs/chunk/{chunk_id}",
    tags=["stereo"],
    response_model=list[schemas.StereoRigSchema.CameraPair],
)
async def read_stereo_cameras_by_chunk(
    session: deps.SessionDep,
    chunk_id: int,
) -> list[schemas.StereoRigSchema.CameraPair]:
    """Reads the stereo camera pairs in a chunk."""
    chunk_model: records.ChunkRecord | None = session.get(records.ChunkRecord, chunk_id)
    if not chunk_model:
        raise HTTPException(404, detail=f"chunk not found: {chunk_id}")
    return chunk_model.stereo_camera_pairs


@router.get(
    "/stereo_camera_tracks/chunk/{chunk_id}",
    tags=["stereo"],
    response_model=list[schemas.StereoCameraTrackSchema],
)
async def read_stereo_tracks_by_chunk(
    session: deps.SessionDep, chunk_id: int
) -> list[schemas.StereoCameraTrackSchema]:
    """Read stereo camera tracks by chunk."""
    chunk_record: records.ChunkRecord | None = session.get(
        records.ChunkRecord, chunk_id
    )
    if not chunk_record:
        raise HTTPException(404, detail=f"chunk not found: {chunk_id}")

    return [
        schemas.StereoCameraTrackSchema.model_validate(track)
        for track in chunk_record.stereo_camera_tracks
    ]
