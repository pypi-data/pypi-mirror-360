"""Module for camera routes."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

import mynd.database as db
import mynd.schemas as schemas
import mynd.records as records

from myndapp.api.dependencies import EngineDep


router: APIRouter = APIRouter()


@router.get("/cameras/chunk/{chunk_id}", tags=["cameras"])
def read_cameras_by_chunk(
    engine: EngineDep, chunk_id: int
) -> list[schemas.CameraSchema]:
    """Read cameras by chunk."""

    with db.Session(engine) as session:
        chunk: records.ChunkRecord | None = session.get(records.ChunkRecord, chunk_id)
        if chunk is None:
            raise HTTPException(404, details=f"chunk not found: {chunk_id}")

        return [schemas.CameraSchema.model_validate(camera) for camera in chunk.cameras]
