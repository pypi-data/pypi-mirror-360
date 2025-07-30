"""Module for mynd CLI database group."""

import click

import mynd.database as db
import mynd.records as records


@click.group()
def database_group() -> None:
    """CLI group for database commands."""
    pass


@database_group.command()
@click.argument("database_name", type=str)
@click.argument("database_host", type=str)
@click.argument("database_port", type=int)
def clear_tables(
    database_name: str,
    database_host: str,
    database_port: int,
) -> None:
    """Clear tables in a database."""
    engine: db.Engine = db.create_engine(
        name=database_name,
        host=database_host,
        port=database_port,
    )
    records.clear_database_tables(engine)


@database_group.command()
@click.argument("database_name", type=str)
@click.argument("database_host", type=str)
@click.argument("database_port", type=int)
def create_tables(
    database_name: str,
    database_host: str,
    database_port: int,
) -> None:
    """Clear tables in a database."""
    engine: db.Engine = db.create_engine(
        name=database_name,
        host=database_host,
        port=database_port,
    )
    records.create_database_tables(engine)
