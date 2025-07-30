"""Module for Mynds router dependencies."""

import functools
import typing

from fastapi import Depends, Request

from myndapp.api.settings import ApplicationSettings
from myndapp.api.image_store import ImageStore

import mynd.database as db

from mynd.utils.log import logger


@functools.lru_cache
def get_settings() -> ApplicationSettings:
    """Returns the application settings. Caches the instance if it has already
    been created."""
    return ApplicationSettings()


ApplicationSettingsDep = typing.Annotated[ApplicationSettings, Depends(get_settings)]


def get_engine(request: Request) -> db.Engine:
    """Returns the application database engine."""
    try:
        engine: db.Engine = request.app.state.engine
        return engine
    except AttributeError as error:
        logger.error(f"error when accessing database engine: {error}")
        raise


EngineDep = typing.Annotated[db.Engine, Depends(get_engine)]


def get_session(request: Request) -> db.Session:
    """Returns the database session."""
    try:
        engine: db.Engine = request.app.state.engine
        with db.Session(engine) as session:
            yield session
    except AttributeError as error:
        logger.error(f"error when accessing database engine: {error}")
        raise


SessionDep = typing.Annotated[db.Session, Depends(get_session)]


def get_image_store(request: Request) -> ImageStore:
    """Retrieves the image store from the application state."""
    try:
        image_store: ImageStore = request.app.state.image_store
        return image_store
    except AttributeError as error:
        logger.error(f"error when accessing application image repository: {error}")
        raise


ImageStoreDep = typing.Annotated[ImageStore, Depends(get_image_store)]
