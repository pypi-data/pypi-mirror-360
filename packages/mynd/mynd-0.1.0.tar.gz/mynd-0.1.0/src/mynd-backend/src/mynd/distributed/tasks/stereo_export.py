"""Module for tasks for exporting stereo data."""

from pathlib import Path
from typing import ClassVar, TypeAlias

from pydantic import BaseModel, Field

import mynd.models.schema as schemas

from mynd.distributed.worker import celery_app
from mynd.image import Image, read_image, write_image
from mynd.utils.containers import Pair

from mynd.geometry.stereo import PixelMap, rectify_image_pair
from mynd.geometry.stereo import StereoMatcher, create_hitnet_matcher
from mynd.geometry.stereo import StereoGeometry, compute_stereo_geometry


ImageFilePair: TypeAlias = Pair[Path]


class StereoExportDirectories(BaseModel):
    """Class representing stereo export directories."""

    images: Path
    ranges: Path
    normals: Path


class StereoExportTask(BaseModel):
    """Class representing"""

    Directories: ClassVar[TypeAlias] = StereoExportDirectories

    directories: Directories = Field(default_factory=StereoExportDirectories)


@celery_app.task
def export_stereo_rectified_images(
    directory: Path,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    image_file_pairs: list[ImageFilePair],
) -> None:
    """Exports stereo rectified images to a directory."""

    assert directory.exists(), f"directory does not exist: {directory}"

    pixel_map_pair: Pair[PixelMap] = Pair(
        first=PixelMap(stereo_rig.pixel_maps.master.to_array()),
        second=PixelMap(stereo_rig.pixel_maps.slave.to_array()),
    )

    for image_file_pair in image_file_pairs:
        image_pair: Pair[Image] = Pair(
            first=read_image(image_file_pair.first),
            second=read_image(image_file_pair.second),
        )

        rectified_image_pair: Pair[Image] = rectify_image_pair(
            images=image_pair, pixel_maps=pixel_map_pair
        )

        write_image(
            rectified_image_pair.first,
            directory / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            rectified_image_pair.second,
            directory / f"{image_file_pair.second.stem}.tiff",
        )


@celery_app.task
def export_stereo_range_maps(
    directories: StereoExportTask.Directories,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    image_file_pairs: list[ImageFilePair],
    matcher_file: Path,
) -> None:
    """Generates stereo range maps by matching a pair of stereo images."""

    assert (
        directories.ranges.exists()
    ), f"directory does not exist: {directories.ranges}"
    assert matcher_file.exists(), f"matcher file does not exist: {matcher_file}"

    stereo_matcher: StereoMatcher = create_hitnet_matcher(matcher_file)

    pixel_map_pair: Pair[PixelMap] = Pair(
        first=PixelMap(stereo_rig.pixel_maps.master.to_array()),
        second=PixelMap(stereo_rig.pixel_maps.slave.to_array()),
    )

    for image_file_pair in image_file_pairs:
        image_pair: Pair[Image] = Pair(
            first=read_image(image_file_pair.first),
            second=read_image(image_file_pair.second),
        )

        rectified_image_pair: Pair[Image] = rectify_image_pair(
            images=image_pair, pixel_maps=pixel_map_pair
        )

        stereo_geometry: StereoGeometry = compute_stereo_geometry(
            sensors_rectified=stereo_rig.sensors_rectified,
            images_rectified=rectified_image_pair,
            matcher=stereo_matcher,
        )

        # TODO: Add callback to export range maps / normal maps
        write_image(
            stereo_geometry.range_maps.first,
            directories.ranges / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            stereo_geometry.range_maps.second,
            directories.ranges / f"{image_file_pair.second.stem}.tiff",
        )


@celery_app.task
def export_stereo_geometry(
    directories: StereoExportTask.Directories,
    stereo_rig: schemas.StereoRigWithMapsSchema,
    image_file_pairs: list[ImageFilePair],
    matcher_file: Path,
) -> None:
    """Export stereo range and normal maps."""

    assert (
        directories.ranges.exists()
    ), f"directory does not exist: {directories.ranges}"
    assert (
        directories.normals.exists()
    ), f"directory does not exist: {directories.normals}"
    assert matcher_file.exists(), f"matcher file does not exist: {matcher_file}"

    stereo_matcher: StereoMatcher = create_hitnet_matcher(matcher_file)

    pixel_map_pair: Pair[PixelMap] = Pair(
        first=PixelMap(stereo_rig.pixel_maps.master.to_array()),
        second=PixelMap(stereo_rig.pixel_maps.slave.to_array()),
    )

    for image_file_pair in image_file_pairs:
        image_pair: Pair[Image] = Pair(
            first=read_image(image_file_pair.first),
            second=read_image(image_file_pair.second),
        )

        rectified_image_pair: Pair[Image] = rectify_image_pair(
            images=image_pair, pixel_maps=pixel_map_pair
        )

        stereo_geometry: StereoGeometry = compute_stereo_geometry(
            sensors_rectified=stereo_rig.sensors_rectified,
            images_rectified=rectified_image_pair,
            matcher=stereo_matcher,
        )

        # Write range maps to file
        write_image(
            stereo_geometry.range_maps.first,
            directories.ranges / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            stereo_geometry.range_maps.second,
            directories.ranges / f"{image_file_pair.second.stem}.tiff",
        )

        # Write normal maps to file
        write_image(
            stereo_geometry.normal_maps.first,
            directories.normals / f"{image_file_pair.first.stem}.tiff",
        )
        write_image(
            stereo_geometry.normal_maps.second,
            directories.normals / f"{image_file_pair.second.stem}.tiff",
        )
