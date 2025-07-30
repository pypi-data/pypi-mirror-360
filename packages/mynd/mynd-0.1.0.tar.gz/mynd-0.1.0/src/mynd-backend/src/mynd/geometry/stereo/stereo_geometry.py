"""Module for estimating stereo geometry, i.e. estimating ranges and normals from image pairs."""

from dataclasses import dataclass
from typing import Callable

from mynd.models.schema import StereoSensorPairSchema
from mynd.image import Image, PixelFormat
from mynd.utils.containers import Pair

from .pixel_map import PixelMap, remap_image_pixels
from .range_map import compute_ranges_from_disparities, compute_normals_from_ranges
from .stereo_matcher import StereoMatcher
from .stereo_rectification import rectify_image_pair


@dataclass
class StereoGeometry:
    """Class representing a stereo geometry."""

    rectified_images: Pair[Image]
    disparities: Pair[Image]
    range_maps: Pair[Image] | None = None
    normal_maps: Pair[Image] | None = None


ImageFilter = Callable[[Image], Image]
DisparityFilter = Callable[[Image], Image]


def compute_stereo_geometry(
    sensors_rectified: StereoSensorPairSchema,
    images_rectified: Pair[Image],
    matcher: StereoMatcher,
    image_filter: ImageFilter | None = None,
    disparity_filter: DisparityFilter | None = None,
) -> StereoGeometry:
    """Computes range and normal maps for a rectified stereo setup, a disparity matcher, and
    a pair of images."""

    if image_filter:
        filtered_images: Pair[Image] = Pair(
            first=image_filter(images_rectified.first),
            second=image_filter(images_rectified.second),
        )
    else:
        filtered_images: Pair[Image] = images_rectified

    # Estimate disparity from rectified images
    disparity_maps: Pair[Image] = matcher(
        left=filtered_images.first,
        right=filtered_images.second,
    )

    if disparity_filter:
        disparity_maps: Pair[Image] = Pair(
            first=disparity_filter(disparity_maps.first),
            second=disparity_filter(disparity_maps.second),
        )

    # Estimate range from disparity
    range_maps: Pair[Image] = Pair(
        first=compute_ranges_from_disparities(
            disparity=disparity_maps.first,
            baseline=sensors_rectified.baseline,
            focal_length=sensors_rectified.master.calibration.focal_length,
        ),
        second=compute_ranges_from_disparities(
            disparity=disparity_maps.second,
            baseline=sensors_rectified.baseline,
            focal_length=sensors_rectified.slave.calibration.focal_length,
        ),
    )

    # Estimate normals from range maps
    normal_maps: Pair[Image] = Pair(
        first=compute_normals_from_ranges(
            range_map=range_maps.first,
            camera_matrix=sensors_rectified.master.calibration.projection_matrix,
            flipped=True,
        ),
        second=compute_normals_from_ranges(
            range_map=range_maps.second,
            camera_matrix=sensors_rectified.slave.calibration.projection_matrix,
            flipped=True,
        ),
    )

    return StereoGeometry(
        rectified_images=images_rectified,
        disparities=disparity_maps,
        range_maps=range_maps,
        normal_maps=normal_maps,
    )


def compute_stereo_range_maps(
    rectified_sensors: StereoSensorPairSchema,
    rectified_images: Pair[Image],
    matcher: StereoMatcher,
    disparity_filter: DisparityFilter | None = None,
) -> Pair[Image]:
    """Computes range maps for a rectified stereo setup."""

    disparity_maps: Pair[Image] = matcher(
        left=rectified_images.first,
        right=rectified_images.second,
    )

    if disparity_filter:
        disparity_maps: Pair[Image] = Pair(
            first=disparity_filter(disparity_maps.first),
            second=disparity_filter(disparity_maps.second),
        )

    master_ranges: Image = compute_ranges_from_disparities(
        disparity=disparity_maps.first,
        baseline=rectified_sensors.baseline,
        focal_length=rectified_sensors.master.calibration.focal_length,
    )

    slave_ranges: Image = compute_ranges_from_disparities(
        disparity=disparity_maps.second,
        baseline=rectified_sensors.baseline,
        focal_length=rectified_sensors.slave.calibration.focal_length,
    )

    return Pair(master_ranges, slave_ranges)


def compute_stereo_normal_maps(
    rectified_sensors: StereoSensorPairSchema,
    range_maps: Pair[Image],
) -> Pair[Image]:
    """Computes stereo normal maps from a pair of rectified sensors and range
    maps."""

    first_normals: Image = compute_normals_from_ranges(
        range_map=range_maps.first,
        camera_matrix=rectified_sensors.master.calibration.projection_matrix,
        flipped=True,
    )

    second_normals: Image = compute_normals_from_ranges(
        range_map=range_maps.second,
        camera_matrix=rectified_sensors.slave.calibration.projection_matrix,
        flipped=True,
    )

    return Pair(first_normals, second_normals)


def distort_stereo_geometry(
    inverse_pixel_maps: Pair[PixelMap],
    range_maps: Pair[Image],
    normal_maps: Pair[Image],
) -> tuple[Pair[Image], ...]:
    """Distorts range and normal maps for the given stereo geometry."""

    distorted_ranges: Pair[Image] = Pair(
        first=remap_image_pixels(
            image=range_maps.first,
            pixel_map=inverse_pixel_maps.first,
        ),
        second=remap_image_pixels(
            image=range_maps.second,
            pixel_map=inverse_pixel_maps.second,
        ),
    )

    distorted_normals: Pair[Image] = Pair(
        first=remap_image_pixels(
            image=normal_maps.first,
            pixel_map=inverse_pixel_maps.first,
        ),
        second=remap_image_pixels(
            image=normal_maps.second,
            pixel_map=inverse_pixel_maps.second,
        ),
    )

    return distorted_ranges, distorted_normals
