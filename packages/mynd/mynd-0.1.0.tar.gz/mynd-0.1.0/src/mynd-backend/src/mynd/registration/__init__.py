"""Package with functionality for registering point clouds."""

from .batch import (
    RegistrationBatch,
    register_batch,
    generate_indices_one_way,
    generate_indices_cascade,
)

from .feature_registrators import (
    extract_fpfh_features,
    register_features_fast,
    register_features_ransac,
)

from .full_registrators import (
    build_pose_graph,
    optimize_pose_graph,
)

from .icp_registrators import (
    register_regular_icp,
    register_colored_icp,
)

from .pipeline import (
    RegistrationPipeline,
    apply_registration_pipeline,
)

from .pipeline_builder import build_registration_pipeline

from .types import (
    Feature,
    RigidTransformation,
    RegistrationResult,
    FeatureExtractor,
    FeatureMatcher,
    PointCloudAligner,
    PointCloudRefiner,
)

from .utilities import log_registration_result


__all__ = [
    "RegistrationBatch",
    "register_batch",
    "generate_indices_one_way",
    "generate_indices_cascade",
    # ...
    "extract_fpfh_features",
    "register_features_fast",
    "register_features_ransac",
    # ...
    "build_pose_graph",
    "optimize_pose_graph",
    # ...
    "register_regular_icp",
    "register_colored_icp",
    # ...
    "RegistrationPipeline",
    "RegistrationCallback",
    "apply_registration_pipeline",
    # ...
    "build_point_cloud_processor",
    "build_ransac_registrator",
    "build_regular_icp_registrator",
    "build_colored_icp_registrator",
    "build_registration_pipeline",
    # ...
    "Feature",
    "RigidTransformation",
    "RegistrationResult",
    "FeatureExtractor",
    "FeatureMatcher",
    "PointCloudAligner",
    "PointCloudRefiner",
    # ...
    "log_registration_result",
]
