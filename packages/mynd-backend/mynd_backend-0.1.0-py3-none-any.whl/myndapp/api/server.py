"""Module for running the backend server."""

from pathlib import Path
from typing import Annotated

import dotenv

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from mynd.config import read_config
from mynd.database import Engine, create_engine, verify_engine
from mynd.utils.log import logger

from .database import load_application_database
from .dependencies import ApplicationSettingsDep, get_settings
from .image_store import ImageStore, create_image_store
from .settings import ApplicationSettings

from .routers import cameras
from .routers import chunks
from .routers import images
from .routers import stereo
from .routers import tasks


app: FastAPI = FastAPI()
app.include_router(cameras.router)
app.include_router(chunks.router)
app.include_router(images.router)
app.include_router(stereo.router)
app.include_router(tasks.router)

settings: ApplicationSettings = get_settings()


# NOTE: Settings can be overridden, i.e. for testing purposes, with the
# following approach:
# app.dependency_overrides[get_settings] = get_settings_override


REQUIRED_ENV_KEYS: list[str] = [
    "PG_DATABASE",
    "PG_HOST",
    "PG_PORT",
    "PG_USERNAME",
    "PG_PASSWORD",
]


@app.on_event("startup")
async def startup_event() -> None:
    """Startup event for FastAPI."""

    settings: ApplicationSettingsDep = get_settings()
    settings.database = read_database_settings(settings.env_file)

    config: dict = read_config(settings.config_file)
    settings.directories = read_application_directories(config)

    image_store: ImageStore = create_image_store(config.get("image_store"))

    engine: Engine = load_application_database(settings)

    logger.info("Server settings:")
    logger.info(f" - Application name:      {settings.app_name}")
    logger.info(f" - Database name:         {settings.database.name}")
    logger.info(f" - Database host:         {settings.database.host}")
    logger.info(f" - Database port:         {settings.database.port}")
    logger.info(f" - Env. file:             {settings.env_file.resolve()}")
    logger.info("")

    logger.info("Image store:")
    logger.info(f" - Total count:           {image_store.total_count()}")
    logger.info(f" - Group count:           {image_store.group_count()}")
    logger.info("")

    error: None | str = verify_engine(engine)
    if error:
        logger.warning(error)
        raise ValueError(f"{error}")

    # Assign objects to application state so we can access them in requests
    app.state.settings = settings
    app.state.engine = engine
    app.state.image_store = image_store


def read_database_settings(env_file: Path) -> ApplicationSettings.Database:
    """Prepares application settings by loading environment variables."""
    assert env_file.exists(), f"env file does not exist: {env_file.resolve()}"

    for key in REQUIRED_ENV_KEYS:
        assert key in dotenv.dotenv_values(env_file), f"missing key in env file: {key}"

    return ApplicationSettings.Database(
        name=dotenv.dotenv_values(env_file).get("PG_DATABASE"),
        host=dotenv.dotenv_values(env_file).get("PG_HOST"),
        port=dotenv.dotenv_values(env_file).get("PG_PORT"),
    )


def read_application_directories(config: dict) -> ApplicationSettings.Directories:
    """Reads application directories from a configuration file."""
    result: dict | None = config.get("server")
    if not result:
        logger.warning(f"error when reading config: {result}")
    return ApplicationSettings.Directories(export=result.get("export_directory"))


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown event for FastAPI."""
    logger.info("From shutdown event.")


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "OK"}


@app.get("/info")
async def info():
    return {
        "app_name": app.state.settings.app_name,
        "database_name": app.state.settings.database.name,
        "database_host": app.state.settings.database.host,
        "database_port": app.state.settings.database.port,
        "verbose": app.state.settings.verbose,
        "engine": str(app.state.engine),
    }
