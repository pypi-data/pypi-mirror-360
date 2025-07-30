"""Module for running the backend server."""

from pathlib import Path

import click
import uvicorn

import myndapp.api.server as server

from mynd.utils.log import logger


@click.group()
def server_group() -> None:
    """Group for server commands."""
    pass


@server_group.command()
@click.option("--host", "server_host", type=str, required=True)
@click.option("--port", "server_port", type=int, required=True)
@click.option("--config", "config_file", type=Path, required=True)
@click.option("--verbose", is_flag=True, default=False)
def run_server(
    server_host: str, server_port: int, config_file: Path, verbose: bool
) -> None:
    """Runs the backend server that holds the database engine. The user
    provides the server host and port through the CLI."""

    assert config_file.exists(), f"config file does not exist: {config_file}"

    logger.info("Running backend server:")
    logger.info(f" - Host:      {server_host}")
    logger.info(f" - Port:      {server_port}")

    settings = server.get_settings()
    settings.verbose = verbose
    settings.config_file = config_file

    uvicorn.run("myndapp.api.server:app", host=server_host, port=server_port)
