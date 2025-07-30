"""Module for camera routes."""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

import mynd.database as db
import mynd.schemas as schemas
import mynd.records as records
import mynd.tasks as tasks

import myndapp.api.dependencies as deps


from mynd.database import Session
from mynd.utils.log import logger

from .camera_base import router


@router.post("/cameras/chunk/{chunk_id}/assimilate", tags=["camera_tasks"])
def assimilate_camera_references(
    engine: deps.EngineDep,
    chunk_id: int,
) -> dict:
    """Assimilates references for stereo camera tracks."""
    _assimilate_camera_references_by_chunk(engine, chunk_id)
    return {"chunk_id": chunk_id}


@router.post("/cameras/batch/assimilate", tags=["camera_tasks"])
def assimilate_camera_references_batch(engine: deps.EngineDep) -> dict:
    """Assimilate camera references for all chunks."""

    with Session(engine) as session:
        chunk_ids: list[int] = list()
        statement = select(records.ChunkRecord)
        chunk_ids: list[int] = [
            chunk_record.id for chunk_record in session.exec(statement).all()
        ]

    response: dict = {"chunk_ids": list()}
    for chunk_id in chunk_ids:
        _assimilate_camera_references_by_chunk(engine, chunk_id)
        response.get("chunk_ids").append(chunk_id)

    return response


def _assimilate_camera_references_by_chunk(
    engine: deps.EngineDep, chunk_id: int
) -> None:
    """Assimilate camera references for a given chunk."""
    with Session(engine) as session:
        chunk_record: records.ChunkRecord | None = session.get(
            records.ChunkRecord, chunk_id
        )
        if chunk_record is None:
            raise HTTPException(404, details=f"chunk not found: {chunk_id}")
        chunk_schema: schemas.ChunkSchema = schemas.ChunkSchema.model_validate(
            chunk_record
        )

    camera_schemas: list[schemas.CameraSchema] = [
        schemas.CameraSchema.model_validate(camera) for camera in chunk_schema.cameras
    ]
    sensor_schemas: list[schemas.SensorSchema] = [
        schemas.SensorSchema.model_validate(sensor) for sensor in chunk_schema.sensors
    ]

    camera_groups: dict[schemas.SensorSchema, list[schemas.CameraSchema]] = {
        sensor: list() for sensor in sensor_schemas
    }

    # Group cameras by sensors
    for camera in camera_schemas:
        camera_groups[camera.sensor].append(camera)

    # We use cameras with prior and estimated references to do the assimilation.
    # To do this reliably we set a threshold of 50 cameras that has to fulfill
    # the criteria.
    TIE_CAMERA_THRESHOLD: int = 50

    selected_groups: list[list[schemas.CameraSchema]] = list()
    for sensor, cameras in camera_groups.items():
        has_prior_and_estimate: list[bool] = [
            camera.prior_reference is not None and camera.aligned_reference is not None
            for camera in cameras
        ]

        if sum(has_prior_and_estimate) > TIE_CAMERA_THRESHOLD:
            selected_groups.append(cameras)

    assimilated_groups: list[schemas.CameraSchema] = list()
    for cameras in selected_groups:
        assimilated_cameras: list[schemas.CameraSchema] = (
            tasks.assimilate_camera_references(cameras)
        )
        assimilated_groups.append(assimilated_cameras)

    # TODO: Update camera records
    for cameras in assimilated_groups:
        _update_assimilated_camera_references(engine, cameras)

    logger.info(f"Assimilated cameras for chunk: {chunk_id}")


def _update_assimilated_camera_references(
    engine: deps.EngineDep, camera_schemas: list[schemas.CameraSchema]
) -> None:
    """Update the assimilated references of a collection of cameras."""

    camera_ids: list[int] = [camera.id for camera in camera_schemas]

    with Session(engine) as session:
        statement = select(records.CameraRecord).where(
            records.CameraRecord.id.in_(camera_ids)
        )
        camera_records: list[records.CameraRecord] = session.exec(statement).all()

        # TODO: Create matchup between schema and record
        camera_record_map: dict[int, records.CameraRecord] = {
            camera.id: camera for camera in camera_records
        }

        # Before we add new references we remove old references
        for camera in camera_records:
            _delete_assimilated_camera_reference(session, camera)

        session.commit()

        # Add new references
        for camera_schema in camera_schemas:
            camera_record: records.CameraRecord | None = camera_record_map.get(
                camera_schema.id
            )

            if camera_record is None:
                continue

            # Add the assimilated reference to the camera
            _add_assimilated_camera_reference(session, camera_schema, camera_record)

        session.commit()


def _delete_assimilated_camera_reference(
    session: Session, camera: records.CameraRecord
) -> None:
    """Deletes an assimilated caemra reference."""
    reference: records.AssimilatedReferenceRecord = camera.assimilated_reference
    camera.assimilated_reference = None

    if reference is not None:
        session.delete(reference)


def _add_assimilated_camera_reference(
    session: Session,
    camera_schema: schemas.CameraSchema,
    camera_record: records.CameraRecord,
) -> None:
    """Adds an assimilated camera reference."""
    reference: records.AssimilatedReferenceRecord = (
        records.AssimilatedReferenceRecord.model_validate(
            camera_schema.assimilated_reference
        )
    )
    camera_record.assimilated_reference = reference
    session.add(reference)
