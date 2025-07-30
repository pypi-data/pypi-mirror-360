"""Module for registration data types."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeAlias

import numpy as np
import open3d

from mynd.geometry.point_cloud import PointCloud


@dataclass
class RegistrationResult:
    """Class representing registration results including the information matrix."""

    fitness: float
    inlier_rmse: float
    correspondence_set: np.ndarray
    transformation: np.ndarray
    information: np.ndarray


# Feature registration interfaces
Feature: TypeAlias = open3d.pipelines.registration.Feature
FeatureExtractor: TypeAlias = Callable[[PointCloud], Feature]
FeatureMatcher: TypeAlias = Callable[
    [PointCloud, PointCloud, Feature, Feature], RegistrationResult
]

# Point cloud registration interfaces
RigidTransformation: TypeAlias = np.ndarray
PointCloudAligner: TypeAlias = Callable[[PointCloud, PointCloud], RegistrationResult]
PointCloudRefiner: TypeAlias = Callable[
    [PointCloud, PointCloud, RigidTransformation], RegistrationResult
]
