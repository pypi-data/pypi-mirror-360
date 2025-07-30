"""Module for point cloud types."""

from collections.abc import Callable
from typing import TypeAlias

import open3d

from mynd.utils.result import Result


PointCloud: TypeAlias = open3d.geometry.PointCloud
PointCloudLoader: TypeAlias = Callable[[None], Result[PointCloud, str]]
PointCloudProcessor = Callable[[PointCloud], PointCloud]
