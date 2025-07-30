"""Module for incremental point cloud registrators."""

import numpy as np
import open3d

from mynd.geometry.point_cloud import PointCloud

import open3d.pipelines.registration as reg

from .types import RegistrationResult, PointCloudRefiner


"""
Worker functions:
 - register_regular_icp
 - register_colored_icp
"""


def register_regular_icp(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    *,
    distance_threshold: float,
    estimation_method: reg.TransformationEstimation = reg.TransformationEstimationPointToPlane(),
    convergence_criteria: reg.ICPConvergenceCriteria = reg.ICPConvergenceCriteria(),
) -> RegistrationResult:
    """Registers the source to the target with ICP."""

    result: reg.RegistrationResult = reg.registration_icp(
        source=source,
        target=target,
        init=transformation,
        max_correspondence_distance=distance_threshold,
        estimation_method=estimation_method,
        criteria=convergence_criteria,
    )

    information: np.ndarray = reg.get_information_matrix_from_point_clouds(
        source=source,
        target=target,
        max_correspondence_distance=distance_threshold,
        transformation=result.transformation,
    )

    return RegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


def register_colored_icp(
    source: PointCloud,
    target: PointCloud,
    transformation: np.ndarray,
    *,
    distance_threshold: float,
    estimation_method: reg.TransformationEstimation = reg.TransformationEstimationForColoredICP(),
    convergence_criteria: reg.ICPConvergenceCriteria = reg.ICPConvergenceCriteria(),
) -> RegistrationResult:
    """Registers the source to the target with ICP."""

    result: reg.RegistrationResult = reg.registration_colored_icp(
        source=source,
        target=target,
        init=transformation,
        max_correspondence_distance=distance_threshold,
        estimation_method=estimation_method,
        criteria=convergence_criteria,
    )

    information: np.ndarray = reg.get_information_matrix_from_point_clouds(
        source=source,
        target=target,
        max_correspondence_distance=distance_threshold,
        transformation=result.transformation,
    )

    return RegistrationResult(
        fitness=result.fitness,
        inlier_rmse=result.inlier_rmse,
        correspondence_set=result.correspondence_set,
        transformation=result.transformation,
        information=information,
    )


"""
Factory functions:
 - create_convergence_criteria_icp
 - create_estimator_point_to_plane
 - create_estimator_icp_generalized
 - create_estimator_icp_colored
 - create_icp_registrator_regular
 - create_icp_registrator_colored
 - create_kernel_loss_huber
 - create_kernel_loss_tukey
"""


def create_convergence_criteria_icp(
    max_iteration: int = 30,
    relative_fitness: float = 1e-06,
    relative_rmse: float = 1e-06,
) -> reg.ICPConvergenceCriteria:
    """Creates a ICP convergence criteria."""
    return reg.ICPConvergenceCriteria(
        max_iteration=max_iteration,
        relative_fitness=relative_fitness,
        relative_rmse=relative_rmse,
    )


def create_estimator_point_to_plane(
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a point to plane transformation estimator."""
    return reg.TransformationEstimationPointToPlane(kernel=kernel)


def create_estimator_icp_generalized(
    epsilon: float,
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a generalized ICP transformation estimator."""
    return reg.TransformationEstimationForGeneralizedICP(epsilon=epsilon, kernel=kernel)


def create_estimator_icp_colored(
    lambda_geometric: float,
    kernel: reg.RobustKernel | None = None,
) -> reg.TransformationEstimation:
    """Creates a colored ICP transformation estimator."""
    return reg.TransformationEstimationForColoredICP(
        lambda_geometric=lambda_geometric,
        kernel=kernel,
    )


def create_icp_registrator_regular(
    estimation_method: reg.TransformationEstimation,
    convergence_criteria: reg.ICPConvergenceCriteria,
    distance_threshold: float,
) -> PointCloudRefiner:
    """Creates a regular ICP registrator from the given arguments."""

    def regular_icp_wrapper(
        source: PointCloud,
        target: PointCloud,
        transformation: np.ndarray,
    ) -> RegistrationResult:
        """Closure wrapper for regular ICP registration method."""
        return register_regular_icp(
            source=source,
            target=target,
            transformation=transformation,
            estimation_method=estimation_method,
            convergence_criteria=convergence_criteria,
            distance_threshold=distance_threshold,
        )

    return regular_icp_wrapper


def create_icp_registrator_colored(
    estimation_method: reg.TransformationEstimation,
    convergence_criteria: reg.ICPConvergenceCriteria,
    distance_threshold: float,
) -> PointCloudRefiner:
    """Creates a colored ICP registrator from the given arguments."""

    def colored_icp_wrapper(
        source: PointCloud,
        target: PointCloud,
        transformation: np.ndarray,
    ) -> RegistrationResult:
        """Closure wrapper for colored ICP registration method."""
        return register_colored_icp(
            source=source,
            target=target,
            transformation=transformation,
            estimation_method=estimation_method,
            convergence_criteria=convergence_criteria,
            distance_threshold=distance_threshold,
        )

    return colored_icp_wrapper


def create_kernel_loss_huber(k: float) -> reg.RobustKernel:
    """Creates a robust kernel with Huber loss."""
    return reg.HuberLoss(k=k)


def create_kernel_loss_tukey(k: float) -> reg.RobustKernel:
    """Creates a robust kernel with Tukey loss."""
    return reg.TukeyLoss(k=k)
