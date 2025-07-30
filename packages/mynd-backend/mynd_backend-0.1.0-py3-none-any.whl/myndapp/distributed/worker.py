"""Module for the Celery instance executing the processing tasks."""

from pathlib import Path

import celery


CELERY_NAME: str = "worker"
CELERY_BACKEND: str = "redis://localhost:6379/0"
CELERY_BROKER: str = "redis://localhost:6379/0"


celery_app: celery.Celery = celery.Celery(
    CELERY_NAME,
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER,
)

# Optional configuration, see the application user guide.
celery_app.conf.update(
    result_expires=3600,
)

# Configure celery to use pickle for serialization / deserialization
celery_app.conf.event_serializer = "pickle"  # this event_serializer is optional.
celery_app.conf.task_serializer = "pickle"
celery_app.conf.result_serializer = "pickle"
celery_app.conf.accept_content = ["application/json", "application/x-python-serialize"]
