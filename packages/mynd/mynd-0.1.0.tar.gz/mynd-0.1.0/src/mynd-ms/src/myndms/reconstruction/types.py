"""Module for reconstruction types."""

from collections.abc import Callable
from typing import TypeAlias

import Metashape as ms


# Interface type for progress callbacks
ProgressCallback = Callable[[float], None]

# Interface type for a chunk processor
ChunkProcessor: TypeAlias = Callable[[ms.Chunk, ProgressCallback], None]
