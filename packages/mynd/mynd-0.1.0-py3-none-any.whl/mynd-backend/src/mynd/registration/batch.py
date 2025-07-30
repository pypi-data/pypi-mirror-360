"""Module for batch registration."""

from collections.abc import Callable, Hashable, Sequence
from dataclasses import dataclass, field
from typing import Generic, TypeAlias, TypeVar

import tqdm

from mynd.geometry.point_cloud import PointCloud, PointCloudLoader

from .pipeline import RegistrationPipeline, apply_registration_pipeline
from .types import RegistrationResult


Key: TypeVar = TypeVar("Key", bound=Hashable)


@dataclass(frozen=True)
class RegistrationBatch(Generic[Key]):
    """Class representing a registration batch."""

    @dataclass(frozen=True)
    class PairIndex:
        """Class representing a pair-wise registration index."""

        target: Key
        source: Key

    @dataclass(frozen=True)
    class PairResult:
        """Class representing a pair-wise registration result."""

        target: Key
        source: Key
        result: RegistrationResult

    @dataclass
    class Result:
        """Class representing a batch registration result."""

        target: Key
        sources: dict[Key, RegistrationResult]

    indices: list[PairIndex] = field(default_factory=list)
    loaders: dict[Key, PointCloudLoader] = field(default_factory=dict)

    def keys(self) -> list[Key]:
        """Returns the keys in the registration batch."""
        return self.loaders.keys()

    def get(self, key: Key) -> PointCloudLoader | None:
        """Returns the point cloud loader or none."""
        return self.loaders.get(key)


def generate_indices_one_way(
    target: Key, sources: Sequence[Key]
) -> list[RegistrationBatch.PairIndex]:
    """Generate a collection of registration indices with a single target."""
    return [
        RegistrationBatch.PairIndex(target, source)
        for source in sources
        if source != target
    ]


def generate_indices_cascade(items: Sequence[Key]) -> list[RegistrationBatch.PairIndex]:
    """Generates a list of cascaded multi-source indices."""

    items: list[Key] = list(items)

    indices: list[RegistrationBatch.PairIndex] = list()
    for index, target in enumerate(items[:-1]):
        sources: list[Key] = items[index + 1 :]

        for source in sources:
            indices.append(RegistrationBatch.PairIndex(target=target, source=source))

    return indices


Batch: TypeAlias = RegistrationBatch
Pipeline: TypeAlias = RegistrationPipeline


Callback: TypeAlias = Callable[[Key, Key, RegistrationResult], None]


def register_batch(
    batch: Batch,
    pipeline: Pipeline,
    # indices: list[Batch.PairIndex],
    callback: Callback | None = None,
) -> list[Batch.PairResult]:
    """Registers a batch of point clouds with the given pipeline."""

    results: list[Batch.PairResult] = list()
    for index in tqdm.tqdm(batch.indices, desc="registering batch..."):
        target_loader: PointCloudLoader = batch.loaders.get(index.target)
        target_cloud: PointCloud = target_loader()

        source_loader: PointCloudLoader = batch.loaders.get(index.source)
        source_cloud: PointCloud = source_loader()

        assert isinstance(target_cloud, PointCloud), "invalid target point cloud"
        assert isinstance(source_cloud, PointCloud), "invalid source point cloud"

        result: RegistrationResult = apply_registration_pipeline(
            pipeline,
            target=target_cloud,
            source=source_cloud,
        )

        if callback is not None:
            callback(index.target, index.source, result)

        pairwise: Batch.PairResult = Batch.PairResult(
            target=index.target, source=index.source, result=result
        )

        results.append(pairwise)

    return results
