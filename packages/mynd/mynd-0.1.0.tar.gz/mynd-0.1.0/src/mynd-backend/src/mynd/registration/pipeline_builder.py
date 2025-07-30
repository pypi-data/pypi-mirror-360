"""Module for building registration pipelines."""

from collections.abc import Callable
from typing import Any, TypeAlias

import open3d.pipelines.registration as reg

from mynd.geometry.point_cloud import PointCloud, PointCloudProcessor
from mynd.geometry.point_cloud import create_downsampler, create_normal_estimator

from .feature_registrators import (
    create_fpfh_extractor,
    create_point_to_point_estimator,
    create_correspondence_validators,
    create_convergence_criteria_ransac,
    create_ransac_registrator,
)

from .icp_registrators import (
    create_kernel_loss_huber,
    create_kernel_loss_tukey,
    create_estimator_point_to_plane,
    create_estimator_icp_colored,
    create_convergence_criteria_icp,
    create_icp_registrator_regular,
    create_icp_registrator_colored,
)

from .types import (
    FeatureExtractor,
    PointCloudAligner,
    PointCloudRefiner,
)

from .pipeline import RegistrationPipeline


Pipeline: TypeAlias = RegistrationPipeline


def build_registration_pipeline(config: dict) -> Pipeline:
    """Builds a registration pipeline from the given config."""

    ALIGNER_KEY: str = "aligner"
    REFINER_KEY: str = "refiner"

    assert ALIGNER_KEY in config, f"missing required key: {ALIGNER_KEY}"
    assert REFINER_KEY in config, f"missing required key: {REFINER_KEY}"

    aligner_module: Pipeline.AlignerModule = _build_aligner_module(
        config.get(ALIGNER_KEY)
    )

    refiner_modules: list[Pipeline.RefinerModule] = [
        _build_refiner_module(section) for section in config.get(REFINER_KEY)
    ]

    return Pipeline(aligner_module, refiner_modules)


def _build_aligner_module(config: dict) -> Pipeline.AlignerModule:
    """Builds an aligner module from the configuration."""

    MATCHER_FACTORIES: list[str] = {
        "feature_ransac": build_ransac_registrator,
    }

    matcher_type: str = config.get("type")
    matcher_params: dict = config.get("matcher")

    preprocessor: PointCloudProcessor = build_point_cloud_processor(
        config.get("preprocessor")
    )

    if matcher_type not in MATCHER_FACTORIES:
        raise NotImplementedError(
            f"invalid alignment matcher - valid options are: {MATCHER_FACTORIES.keys()}"
        )

    factory = MATCHER_FACTORIES.get(matcher_type)
    matcher: PointCloudAligner = factory(matcher_params)

    return Pipeline.AlignerModule(preprocessor, matcher)


def _build_refiner_module(config: dict) -> Pipeline.RefinerModule:
    """Builds an refiner module from the configuration."""

    REFINER_FACTORIES: dict[str, Callable] = {
        "regular_icp": build_regular_icp_registrator,
        "colored_icp": build_colored_icp_registrator,
    }

    preprocessor: PointCloudProcessor = build_point_cloud_processor(
        config.get("preprocessor")
    )

    matcher_type: str = config.get("type")
    matcher_params: str = config.get("matcher")

    factory = REFINER_FACTORIES.get(matcher_type)
    matcher: PointCloudRefiner = factory(matcher_params)

    return Pipeline.RefinerModule(preprocessor, matcher)


def build_point_cloud_processor(components: dict[str, Any]) -> PointCloudProcessor:
    """Builds a point cloud preprocessor from a configuration."""

    processors: list[PointCloudProcessor] = list()

    if "downsample" in components:
        processors.append(create_downsampler(**components.get("downsample")))

    if "estimate_normals" in components:
        processors.append(create_normal_estimator(**components.get("estimate_normals")))

    def preprocess_point_cloud(cloud: PointCloud) -> PointCloud:
        """Preprocesses a point cloud."""
        processed: PointCloud = cloud
        for processor in processors:
            processed: PointCloud = processor(processed)

        return processed

    return preprocess_point_cloud


def build_ransac_registrator(components: dict[str, Any]) -> PointCloudAligner:
    """Builds a RANSAC registrator from a collection of parameters."""

    for key in [
        "feature",
        "point_to_point",
        "validators",
        "convergence",
        "algorithm",
    ]:
        assert key in components, f"missing build component: {key}"

    feature_extractor: FeatureExtractor = create_fpfh_extractor(
        **components.get("feature")
    )
    estimation_method = create_point_to_point_estimator(
        **components.get("point_to_point")
    )
    validators = create_correspondence_validators(**components.get("validators"))
    convergence_criteria = create_convergence_criteria_ransac(
        **components.get("convergence")
    )

    return create_ransac_registrator(
        feature_extractor=feature_extractor,
        estimation_method=estimation_method,
        validators=validators,
        convergence_criteria=convergence_criteria,
        **components.get("algorithm"),
    )


def build_regular_icp_registrator(
    parameters: dict,
) -> PointCloudRefiner:
    """Builds a regular ICP registrator from a configuration."""

    if BUILD_HUBER_KEY in parameters:
        kernel: reg.RobustKernel = create_kernel_loss_huber(
            **parameters.get(BUILD_HUBER_KEY)
        )
    elif BUILD_TUKEY_KEY in parameters:
        kernel: reg.RobustKernel = create_kernel_loss_tukey(
            **parameters.get(BUILD_TUKEY_KEY)
        )
    else:
        kernel = None

    # NOTE: For now we only use a point to plane estimator for regular ICP
    estimator: reg.TransformationEstimation = create_estimator_point_to_plane(
        kernel=kernel
    )

    if CONVERGENCE_CRITERIA_KEY in parameters:
        convergence_criteria: reg.ICPConvergenceCriteria = (
            create_convergence_criteria_icp(**parameters.get(CONVERGENCE_CRITERIA_KEY))
        )
    else:
        convergence_criteria: reg.ICPConvergenceCriteria = (
            create_convergence_criteria_icp()
        )

    if DISTANCE_THRESHOLD_KEY not in parameters:
        raise ValueError(f"regular icp builder: missing key '{DISTANCE_THRESHOLD_KEY}'")

    distance_threshold: float = parameters.get("distance_threshold")

    return create_icp_registrator_regular(
        estimation_method=estimator,
        convergence_criteria=convergence_criteria,
        distance_threshold=distance_threshold,
    )


# TODO: Add named tuple to hold build keys
BUILD_HUBER_KEY: str = "huber_kernel"
BUILD_TUKEY_KEY: str = "tukey_kernel"
CONVERGENCE_CRITERIA_KEY: str = "convergence_criteria"
DISTANCE_THRESHOLD_KEY: str = "distance_threshold"


def build_colored_icp_registrator(
    parameters: dict,
) -> PointCloudRefiner:
    """Builds an incremental registrator from a configuration."""

    COLOR_ESTIMATOR_KEY: str = "colored_icp_estimation"

    if BUILD_HUBER_KEY in parameters:
        kernel: reg.RobustKernel = create_kernel_loss_huber(
            **parameters.get(BUILD_HUBER_KEY)
        )
    elif BUILD_TUKEY_KEY in parameters:
        kernel: reg.RobustKernel = create_kernel_loss_tukey(
            **parameters.get(BUILD_TUKEY_KEY)
        )
    else:
        kernel = None

    if COLOR_ESTIMATOR_KEY in parameters:
        estimator: reg.TransformationEstimation = create_estimator_icp_colored(
            **parameters.get(COLOR_ESTIMATOR_KEY),
            kernel=kernel,
        )
    else:
        raise ValueError(f"colored icp builder: missing key '{COLOR_ESTIMATOR_KEY}'")

    if CONVERGENCE_CRITERIA_KEY in parameters:
        criteria: reg.ICPConvergenceCriteria = create_convergence_criteria_icp(
            **parameters.get(CONVERGENCE_CRITERIA_KEY),
        )

    if DISTANCE_THRESHOLD_KEY not in parameters:
        raise ValueError(f"colored icp builder: missing key '{DISTANCE_THRESHOLD_KEY}'")

    distance_threshold: float = parameters.get(DISTANCE_THRESHOLD_KEY)

    return create_icp_registrator_colored(
        estimation_method=estimator,
        convergence_criteria=criteria,
        distance_threshold=distance_threshold,
    )
