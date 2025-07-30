"""Module for sparse and dense reconstruction processors."""

from collections.abc import Callable

import Metashape as ms

from mynd.utils.log import logger
from mynd.utils.result import Ok, Err, Result

from .types import ChunkProcessor, ProgressCallback
from .utils import progress_bar, stdout_redirected


IMAGE_MATCH_PARAMETERS = {
    "quality": int,  # NOTE: 0: "highest", 1: "high", 2: "medium", 3: "low", 4: "lowest"
    "generic_preselection": bool,  #
    "reference_preselection": bool,
    "keypoint_limit": int,
    "tiepoint_limit": int,
    "pairs": list[tuple[int, int]],
    "cameras": list[int],
    "reset_matches": bool,
}

CAMERA_ALIGN_PARAMETERS = {
    "cameras": list[int],
    "point_clouds": list[int],
    "min_image": int,
    "adaptive_fitting": bool,
    "reset_alignment": bool,
    "subdivide_task": bool,
}

CAMERA_OPTIMIZE_PARAMETERS = {
    "fit_f": bool,
    "fit_cx": bool,  # Enable optimization of X principal point coordinates.
    "fit_cy": bool,  # Enable optimization of Y principal point coordinates.
    "fit_b1": bool,  # Enable optimization of aspect ratio.
    "fit_b2": bool,  # Enable optimization of skew coefficient.
    "fit_k1": bool,  # Enable optimization of k1 radial distortion coefficient.
    "fit_k2": bool,  # Enable optimization of k2 radial distortion coefficient.
    "fit_k3": bool,  # Enable optimization of k3 radial distortion coefficient.
    "fit_k4": bool,  # Enable optimization of k3 radial distortion coefficient.
    "fit_p1": bool,  # Enable optimization of p1 tangential distortion coefficient.
    "fit_p2": bool,  # Enable optimization of p2 tangential distortion coefficient.
    "fit_corrections": bool,  # Enable optimization of additional corrections.
    "adaptive_fitting": bool,  # Enable adaptive fitting of distortion coefficients.
    "tiepoint_covariance": bool,  # Estimate tie point covariance matrices.
}

SPARSE_PROCESSOR_PARAMETERS: dict[str, dict] = {
    "match_images": IMAGE_MATCH_PARAMETERS,
    "align_cameras": CAMERA_ALIGN_PARAMETERS,
    "optimize_cameras": CAMERA_OPTIMIZE_PARAMETERS,
}


def get_sparse_processor_info() -> dict[str, dict]:
    """Returns the sparse processors for the backend."""
    return SPARSE_PROCESSOR_PARAMETERS


def match_images(
    chunk: ms.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback,
) -> Result[None, str]:
    """Matches the images in the chunk."""

    # TODO: Map reference preselection mode to Metashapes options
    with stdout_redirected():
        try:
            chunk.matchPhotos(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def align_cameras(
    chunk: ms.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback,
) -> Result[None, str]:
    """Aligns the cameras in the chunk."""
    with stdout_redirected():
        try:
            chunk.alignCameras(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def optimize_cameras(
    chunk: ms.Chunk,
    parameters: dict,
    progress_fun: ProgressCallback,
) -> Result[None, str]:
    """Optimizes the calibration and camera poses in the chunk."""
    with stdout_redirected():
        try:
            chunk.optimizeCameras(**parameters, progress=progress_fun)
        except BaseException as error:
            return Err(error)

    return Ok(None)


def build_sparse_processors(configs: list[dict]) -> list[ChunkProcessor]:
    """Builds a collection of sparse processors from configurations."""

    processors: list[ChunkProcessor] = list()
    for config in configs:
        processor: ChunkProcessor | None = _build_sparse_processor(config)
        if processor is None:
            continue
        processors.append(processor)

    return processors


def _build_sparse_processor(config: dict) -> ChunkProcessor | None:
    """Builds a sparse processor from the given configuration."""

    processor_type: str = config.get("process")
    enabled: bool = config.get("enabled")
    parameters: dict = config.get("parameters")

    if not enabled:
        return None

    factories: dict[str, Callable] = {
        "match_images": create_image_matcher,
        "align_cameras": create_camera_aligner,
        "optimize_cameras": create_camera_optimizer,
    }

    assert processor_type in factories, f"invalid sparse processor: {processor_type}"
    factory: Callable = factories.get(processor_type)
    return factory(parameters=parameters)


def create_image_matcher(parameters: dict) -> ChunkProcessor:
    """Creates an image matcher."""

    @progress_bar(description="Matching images...")
    def image_matcher_wrapper(
        chunk: ms.Chunk, progress_fun: ProgressCallback = lambda x: None
    ) -> None:
        """Wraps an image matcher."""
        return match_images(chunk, parameters=parameters, progress_fun=progress_fun)

    return image_matcher_wrapper


def create_camera_aligner(parameters: dict) -> ChunkProcessor:
    """Creates a camera aligner."""

    @progress_bar(description="Aligning cameras...")
    def camera_aligner_wrapper(
        chunk: ms.Chunk, progress_fun: ProgressCallback = lambda x: None
    ) -> None:
        """Wraps a camera aligner."""
        return align_cameras(chunk, parameters=parameters, progress_fun=progress_fun)

    return camera_aligner_wrapper


def create_camera_optimizer(parameters: dict) -> ChunkProcessor:
    """Creates a camera optimizer."""

    @progress_bar(description="Optimizing cameras...")
    def camera_optimizer_wrapper(
        chunk: ms.Chunk, progress_fun: ProgressCallback = lambda x: None
    ) -> None:
        """Wraps a camera optimizer."""
        return optimize_cameras(chunk, parameters=parameters, progress_fun=progress_fun)

    return camera_optimizer_wrapper
