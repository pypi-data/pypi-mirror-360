"""Module for exporting dense products."""

from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias

import Metashape as ms

from mynd.geometry.point_cloud import PointCloudLoader, create_point_cloud_loader


ProgressCallback: TypeAlias = Callable[[float], None]


def export_dense_cloud(
    chunk: ms.Chunk,
    path: str | Path,
    progress_fun: ProgressCallback = lambda percent: None,
) -> Path | str:
    """Exports a point cloud from a Metashape chunk to a file."""

    try:
        chunk.exportPointCloud(
            path=str(path),  # Path to output file.
            source_data=ms.DataSource.PointCloudData,
            binary=False,  # NOTE: True,
            save_point_normal=True,
            save_point_color=True,
            save_point_classification=False,
            save_point_confidence=False,
            save_comment=False,
            progress=progress_fun,
        )
    except BaseException as error:
        return str(error)

    return Path(path)


def export_raster(
    chunk: ms.Chunk,
    path: str | Path,
    progress_fun: ProgressCallback = lambda percent: None,
) -> Path | str:
    """Exports a point cloud from a Metashape chunk to a file."""

    try:
        chunk.exportRaster(
            path=str(path),  # Path to output file.
            format=ms.RasterFormatTiles,
            image_format=ms.ImageFormatNone,
            raster_transform=ms.RasterTransformNone,
            resolution=0,
            resolution_x=0,
            resolution_y=0,
            block_width=10000,
            block_height=10000,
            progress=progress_fun,
        )
    except BaseException as error:
        return str(error)

    return Path(path)


def retrieve_dense_cloud_loader(
    chunk: ms.Chunk,
    cache: Path,
    force_overwrite: bool,
) -> dict[int, PointCloudLoader]:
    """Retrieves the dense points from the current project.

    :arg document:      Metashape document
    :arg cache:         cache directory for exported products
    :arg overwrite:     overwrite exported products
    """

    # Export point cloud or retrieve point cloud path
    output_path: Path = cache / f"{chunk.label}.ply"
    if output_path.exists() and not force_overwrite:
        point_cloud_path: Path = output_path
    else:
        point_cloud_path: Path | str = export_dense_cloud(chunk, path=output_path)

    return create_point_cloud_loader(source=point_cloud_path)
