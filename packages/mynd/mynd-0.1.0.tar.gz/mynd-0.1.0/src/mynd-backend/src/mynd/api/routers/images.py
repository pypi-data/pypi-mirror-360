"""Module for FastAPI image file routers."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from mynd.utils.log import logger

from mynd.api.dependencies import ImageStoreDep
from mynd.api.image_store import ImageStore


router = APIRouter()


@router.get("/images/all", tags=["images"], response_model=list[str])
async def read_images(store: ImageStoreDep) -> list[str]:
    """Reads the images from the image store."""
    files: list[str] = list()
    for group in store.iter_groups():
        files.extend([str(path) for path in group.paths])
    return files


@router.get("/images/stats", tags=["images"], response_model=dict)
async def read_image_statistics(store: ImageStoreDep) -> dict:
    """Reads statistics for the image store."""
    group_stats: list[dict] = [
        {
            "name": group.name,
            "count": group.file_count(),
            "root": group.config.root,
            "suffixes": group.config.suffixes,
        }
        for group in store.iter_groups()
    ]

    return {
        "total_count": store.total_count(),
        "groups": group_stats,
    }


@router.get("/images/groups", tags=["images"])
async def read_image_groups(store: ImageStoreDep) -> list[str]:
    """Reads the groups in the image store."""
    return store.group_names()


@router.get("/images/group/{file_group_name}", tags=["images"])
async def read_group_images(store: ImageStoreDep, file_group_name: str) -> list[Path]:
    """Reads images from an image store group."""
    group: ImageStore.FileGroup | None = store.get_group(file_group_name)
    if group is None:
        raise HTTPException(404, detail=f"image group not found: {file_group_name}")
    return group.paths


@router.get(
    "/images/{file_group_name}/{file_name}",
    tags=["images"],
    response_class=FileResponse,
)
async def read_image(
    store: ImageStoreDep, file_group_name: str, file_name: str
) -> FileResponse:
    """Reads the images from the image store."""
    group: ImageStore.FileGroup | None = store.get_group(file_group_name)

    if not group:
        raise HTTPException(404, detail=f"file group not found: {file_group_name}")

    image_file: Path | None = group.get_file(file_name)
    if not image_file.exists():
        raise HTTPException(404, detail=f"file does not exist: {image_file}")

    media_type: str = f"image/{image_file.suffix.strip(".")}"
    return FileResponse(image_file, filename=image_file.name, media_type=media_type)
