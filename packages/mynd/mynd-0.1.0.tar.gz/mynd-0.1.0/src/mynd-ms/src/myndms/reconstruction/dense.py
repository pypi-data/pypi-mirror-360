"""Module that implements the dense service for the Metashape backend."""

from collections.abc import Callable
from functools import partial
from pathlib import Path

import Metashape as ms

from .types import ProgressCallback
from .utils import stdout_redirected


"""
Dense processors:
 - build_depth_maps
 - build_point_cloud
 - build_mesh
 - build_coordinate_map
 - build_texture
"""


def build_depth_maps(
    chunk: ms.Chunk,
    progress_fun: ProgressCallback,
    parameters: dict,
) -> None | str:
    """Builds depth maps for the given chunk."""
    with stdout_redirected():
        try:
            chunk.buildDepthMaps(
                **parameters,
                filter_mode=ms.MildFiltering,
                progress=progress_fun,
            )
        except BaseException as error:
            return str(error)


def build_point_cloud(
    chunk: ms.Chunk,
    progress_fun: ProgressCallback,
    parameters: dict,
) -> None | str:
    """Builds a dense point cloud for the given chunk."""
    with stdout_redirected():
        try:
            chunk.buildPointCloud(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return str(error)


def build_mesh(
    chunk: ms.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback,
) -> None | str:
    """Builds a mesh model for the given chunk."""
    # TODO: Add mapping for Metashape internal argument types
    with stdout_redirected():
        try:
            chunk.buildModel(
                source_data=ms.DepthMapsData,
                surface_type=ms.Arbitrary,
                interpolation=ms.EnabledInterpolation,
                progress=progress_fun,
            )
        except BaseException as error:
            return str(error)


def build_coordinate_map(
    chunk: ms.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback = None,
) -> None | str:
    """Builds a coordinate map for the given chunk."""
    # TODO: Add conversion support for the following type: ms.GenericMapping,
    with stdout_redirected():
        try:
            chunk.buildUV(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return str(error)


def build_texture(
    chunk: ms.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback = None,
) -> None | str:
    """Builds a model texture for the given chunk."""
    # TODO: Add conversion support for the following type: ms.MosaicBlending,
    with stdout_redirected():
        try:
            chunk.buildTexture(
                **parameters,
                progress=progress_fun,
            )
        except BaseException as error:
            return str(error)


DENSE_PROCESSORS = {
    "build_depth_maps": build_depth_maps,
    "build_point_cloud": build_point_cloud,
    "build_mesh": build_mesh,
    "build_coordinate_map": build_coordinate_map,
    "build_texture": build_texture,
}


def build_dense_processor(config: dict) -> Callable | str:
    """Builds a dense processor from a configuration."""

    processor: str = config["process"]
    _enabled: bool = config["enabled"]
    parameters: dict = config["parameters"]

    match processor:
        case "build_depth_maps":
            return partial(build_depth_maps, parameters=parameters)
        case "build_point_cloud":
            return partial(build_point_cloud, parameters=parameters)
        case "build_texture":
            return partial(build_texture, parameters=parameters)
        case _:
            return f"invalid processor: {processor}"
