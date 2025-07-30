"""Module for running backend instances."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from mynd.models.schema import ChunkSchema, ChunkGroupSchema
from mynd.models.record import ChunkRecord, ChunkGroupRecord

from mynd.api.dependencies import SessionDep


router = APIRouter()


@router.get("/chunk_groups", tags=["chunks"], response_model=list[int])
async def read_chunk_group_ids(session: SessionDep) -> list[int]:
    """Reads the chunk group ids in the database."""
    chunk_groups: list[ChunkGroupRecord] = session.exec(select(ChunkGroupRecord)).all()
    return [group.id for group in chunk_groups]


@router.put(
    "/chunk_groups/{group_id}", tags=["chunks"], response_model=ChunkGroupSchema
)
async def update_chunk_group(session: SessionDep, group_id: int) -> ChunkGroupSchema:
    """Updates a chunk group in the database."""
    chunk_group: ChunkGroupRecord | None = session.get(ChunkGroupRecord, group_id)
    if not chunk_group:
        raise HTTPException(404, detail="chunk group not found")
    return chunk_group


@router.get("/chunks/all", tags=["chunks"], response_model=dict[int, str])
async def read_chunk_labels(session: SessionDep) -> dict[int, str]:
    """Reads the chunk group ids in the database."""
    chunks: list[ChunkRecord] = session.exec(select(ChunkRecord)).all()
    return {chunk.id: chunk.label for chunk in chunks}


@router.get("/chunks/{chunk_id}", tags=["chunks"], response_model=ChunkSchema)
async def read_chunk(session: SessionDep, chunk_id: int) -> ChunkSchema:
    """Reads the chunks in the database."""
    chunk_model: ChunkRecord | None = session.get(ChunkRecord, chunk_id)
    if not chunk_model:
        raise HTTPException(404, detail="chunk not found")
    return chunk_model
