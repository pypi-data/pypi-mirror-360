"""Module for handling reconstruction tasks."""

import Metashape as ms
import tqdm

from mynd.utils.log import logger

from .types import ChunkProcessor, ProgressCallback
from .sparse import get_sparse_processor_info
from .sparse import build_sparse_processors


def handle_reconstruction_task(
    document: ms.Document,
    chunk_labels: tuple[str],
    config: dict,
) -> None:
    """Handles a reconstruction task."""

    assert "sparse" in config, "missing configuration key 'sparse'"
    assert "dense" in config, "missing configuration key 'dense'"

    # TODO: Build pipeline
    # TODO: Invoke reconstruction task

    # Build sparse processor based on the entries in the configuration
    sparse_processors: list[ChunkProcessor] = build_sparse_processors(
        config.get("sparse")
    )

    # NOTE: Select a single chunk for now
    chunk: ms.Chunk = document.chunks[0]

    for processor in sparse_processors:
        processor(chunk)
