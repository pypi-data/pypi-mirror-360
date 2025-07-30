"""Module for working with Mynd documents in the CLI."""

from pathlib import Path

import click

from loguru import logger
from sqlmodel import select

import mynd.config as conf
import mynd.database as db
import mynd.schemas as schemas
import mynd.records as records
import mynd.utils.env as env

from .group import group


@group.command()
@click.argument("database", type=str)
@click.argument("host", type=str)
@click.argument("port", type=int)
@click.argument("output", type=Path)
@click.option("--document", "document_ids", type=int, multiple=True)
@click.option("--all", "select_all", is_flag=True, default=False, type=bool)
def export_document(
    database: str,
    host: str,
    port: int,
    output: Path,
    document_ids: list[int],
    select_all: bool,
) -> None:
    """Reads a document from the database and exports it to file."""

    assert "PG_USERNAME" in env.values(), "missing username in .env file"
    assert "PG_PASSWORD" in env.values(), "missing password in .env file"
    assert output.parent.exists(), f"directory does not exist: {output.parent}"

    engine: db.Engine = db.create_engine(database, host, port)

    if select_all:
        document_ids: list[int] = get_document_ids(engine)

    for document_id in document_ids:
        handle_document_export(engine, document_id, output)


def get_document_ids(engine: db.Engine) -> list[int]:
    """Gets all document ids from the given engine."""
    with db.Session(engine) as session:
        results: list = session.exec(select(records.ChunkGroupRecord))
        return [result.id for result in results]


def handle_document_export(engine: db.Engine, document_id: int, output: Path) -> None:
    """Handles exporting of a document, including reading, converting, and writing."""

    with db.Session(engine) as session:
        record: list[records.ChunkGroupRecord] | None = session.get(
            records.ChunkGroupRecord, document_id
        )

        if record is None:
            logger.warning(f"unable to find document with id: {document_id}")
            return

        schema: schemas.ChunkGroupSchema = schemas.ChunkGroupSchema.model_validate(
            record
        )

        logger.info("Document:")
        logger.info(f" - ID:            {schema.id}")
        logger.info(f" - Label:         {schema.label}")
        logger.info(f" - Chunks:        {len(schema.chunks)}")

        for chunk in schema.chunks:
            logger.info(f"Chunk: {chunk.id} - {chunk.label}")
            logger.info(f" - Cameras:           {len(chunk.cameras)}")
            logger.info(f" - Stereo rigs:       {len(chunk.stereo_rigs)}")
            logger.info(f" - Stereo cameras:    {len(chunk.stereo_camera_pairs)}")

        destination: Path = output / f"{schema.label}.json"
        result: Path | str = conf.write_config(destination, schema.model_dump())

        if isinstance(result, Path):
            logger.info(f"Wrote document to path: {result}")
        else:
            logger.error(f"Error when writing document: {result}")
