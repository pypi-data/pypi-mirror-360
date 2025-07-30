"""Module for executing registration tasks."""

import time

from collections.abc import Callable

from mynd.geometry.point_cloud import PointCloud, PointCloudLoader
from mynd.registration import RegistrationPipeline, RegistrationResult
from mynd.registration import RegistrationBatch, register_batch
from mynd.visualization.render import visualize_registration

from mynd.utils.log import logger
from mynd.utils.result import Ok, Result


def register_chunks(
    batch: RegistrationBatch[int],
    pipeline: RegistrationPipeline,
    reference: int,
    visualize: bool = False,
    callback: Callable | None = None,
) -> RegistrationBatch.Result:
    """Registers a batch of groups with the given"""

    logger.info("")
    logger.info("Performing batch registration...")
    start: float = time.time()
    registration_results: list[RegistrationBatch.PairResult] = register_batch(
        batch,
        pipeline,
        callback=callback,
    )
    end: float = time.time()
    logger.info(f"Registered batch in {end-start:.2f} seconds!")
    logger.info("")

    if visualize:
        for registration in registration_results:
            target_loader: PointCloudLoader | None = batch.get(registration.target)
            source_loader: PointCloudLoader | None = batch.get(registration.source)

            target_cloud: PointCloud = target_loader().unwrap()
            source_cloud: PointCloud = source_loader().unwrap()

            visualize_registration(
                target=target_cloud,
                source=source_cloud,
                transformation=registration.result.transformation,
            )

    batch_result: RegistrationBatch.Result = reference_registration_results(
        target=reference, pairwise_result=registration_results
    )

    return batch_result


def reference_registration_results(
    target: int, pairwise_result: list[RegistrationBatch.PairResult]
) -> RegistrationBatch.Result:
    """Reference a collection of registration results to a target."""

    source_results: dict[int, RegistrationResult] = dict()

    for pairwise in pairwise_result:
        if pairwise.target == target:
            source_results[pairwise.source] = pairwise.result

    return RegistrationBatch.Result(target=target, sources=source_results)
