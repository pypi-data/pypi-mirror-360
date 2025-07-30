"""Module for registration CLI entrypoints."""

from pathlib import Path
from typing import TypeAlias

import Metashape as ms

from mynd.geometry.point_cloud import PointCloudLoader
from mynd.registration import RegistrationBatch
from mynd.registration import RegistrationPipeline
from mynd.registration import build_registration_pipeline
from mynd.registration import generate_indices_cascade
from mynd.registration import generate_indices_one_way
from mynd.utils.log import logger

from myndms.helpers import retrieve_dense_cloud_loader

from .update import register_chunk_pair
from .worker import register_chunks


def handle_chunk_registration(
    document: ms.Document,
    config: dict,
    cache: Path,
    reference_label: str | None = None,
    visualize: bool = False,
    force_export: bool = False,
) -> None:
    """Handles chunk registration. This includes preparing point cloud loaders,
    selecting a reference chunk, building a registration pipeline, and
    performing batch registration."""

    Key: TypeAlias = int

    selected_chunks: list[ms.Chunk] = [
        chunk for chunk in document.chunks if chunk.enabled
    ]

    # To perform the registration, we retrieve the dense point clouds for each chunk
    point_cloud_loaders: dict[Key, PointCloudLoader] = {
        chunk.key: retrieve_dense_cloud_loader(chunk, cache, force_export)
        for chunk in selected_chunks
    }

    # To find a common reference for the registration, we select a single chunk
    reference_chunk: ms.Chunk = retrieve_reference_chunk(
        reference_label,
        selected_chunks,
    )

    pipeline: RegistrationPipeline = build_registration_pipeline(config)

    INDEX_STRATEGY: str = "one-way"
    match INDEX_STRATEGY:
        case "one-way":
            indices: list[RegistrationBatch.PairIndex] = generate_indices_one_way(
                reference_chunk.key,
                [chunk.key for chunk in selected_chunks],
            )
        case "cascade":
            indices: list[RegistrationBatch.PairIndex] = generate_indices_cascade(
                [chunk.key for chunk in selected_chunks],
            )
        case _:
            raise NotImplementedError

    batch: RegistrationBatch = RegistrationBatch[Key](
        indices=indices,
        loaders=point_cloud_loaders,
    )

    batch_result: RegistrationBatch.Result = register_chunks(
        batch, pipeline, reference=reference_chunk.key, visualize=visualize
    )

    # NOTE: We use chunk keys to map chunks to results, since chunks are unhashable
    target: int = batch_result.target

    chunk_map: dict[int, ms.Chunk] = {chunk.key: chunk for chunk in document.chunks}

    for source, result in batch_result.sources.items():
        target_chunk: ms.Chunk | None = chunk_map.get(target)
        source_chunk: ms.Chunk | None = chunk_map.get(source)

        if target_chunk is None or source_chunk is None:
            continue

        register_chunk_pair(target_chunk, source_chunk, result)


def retrieve_reference_chunk(
    reference_label: str, chunks: list[ms.Chunk]
) -> ms.Chunk | None:
    """Retrieves a reference chunk based on the chunk label."""

    chunk_map: dict[str, ms.Chunk] = {chunk.label: chunk for chunk in chunks}

    if reference_label not in chunk_map:
        logger.error(f"missing reference label: {reference_label}")
        exit()

    reference_chunk: ms.Chunk = chunk_map.get(reference_label)
    return reference_chunk
