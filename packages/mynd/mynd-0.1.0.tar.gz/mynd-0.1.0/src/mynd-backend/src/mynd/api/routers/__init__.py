"""Package with various API router modules."""

from .cameras import camera_router
from .chunks import router as chunk_router
from .images import router as image_router
from .stereo_crud import router as stereo_crud_router
from .stereo_tasks import router as stereo_task_router
from .tasks import router as task_router


__all__ = [
    "camera_router",
    "chunk_router",
    "image_router",
    "stereo_crud_router",
    "stereo_task_router",
    "task_router",
]
