"""Module for application database."""

import dotenv

from myndapp.api.settings import ApplicationSettings

from mynd.database import Engine, create_engine


def load_application_database(settings: ApplicationSettings) -> Engine:
    """Loads the database engine for an application."""
    return create_engine(
        name=settings.database.name,
        host=settings.database.host,
        port=settings.database.port,
        username=dotenv.dotenv_values(settings.env_file).get("PG_USERNAME"),
        password=dotenv.dotenv_values(settings.env_file).get("PG_PASSWORD"),
        echo=settings.verbose,
    )
