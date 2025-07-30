"""Module for point cloud IO, i.e. reading and writing point clouds."""

from pathlib import Path

import open3d

from .point_cloud_types import PointCloud, PointCloudLoader


def read_point_cloud(path: str | Path) -> PointCloud | str:
    """Loads a point cloud from a file."""
    try:
        point_cloud: PointCloud = open3d.io.read_point_cloud(str(path))
        return point_cloud
    except IOError as error:
        return str(error)


def create_point_cloud_loader(source: str | Path) -> PointCloudLoader:
    """Creates a point cloud loader for the source."""

    def load_point_cloud() -> PointCloud | str:
        """Loads a point cloud from the source."""
        return read_point_cloud(path=source)

    return load_point_cloud
