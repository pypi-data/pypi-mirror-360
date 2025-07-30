"""Module for camera routes."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

import mynd.models.schema as schemas
import mynd.models.record as records

from mynd.api.dependencies import EngineDep
from mynd.database import Session


camera_router: APIRouter = APIRouter()


@camera_router.get("/cameras/chunk/{chunk_id}", tags=["cameras"])
def read_cameras_by_chunk(
    engine: EngineDep, chunk_id: int
) -> list[schemas.CameraSchema]:
    """Read cameras by chunk."""

    with Session(engine) as session:
        chunk: records.ChunkRecord | None = session.get(records.ChunkRecord, chunk_id)
        if chunk is None:
            raise HTTPException(404, details=f"chunk not found: {chunk_id}")

        return [schemas.CameraSchema.model_validate(camera) for camera in chunk.cameras]


@camera_router.get("/camera_tracks/chunk/{chunk_id}", tags=["cameras"])
def read_camera_tracks_by_chunk(
    engine: EngineDep, chunk_id: int
) -> list[schemas.CameraTrackSchema]:
    """Read camera tracks by chunk."""
    with Session(engine) as session:
        chunk: records.ChunkRecord | None = session.get(records.ChunkRecord, chunk_id)
        if chunk is None:
            raise HTTPException(404, details=f"chunk not found: {chunk_id}")

        return [
            schemas.CameraTrackSchema.model_validate(camera_track)
            for camera_track in chunk.camera_tracks
        ]
