"""Module for running the backend worker."""

import click

from myndapp.distributed.worker import celery_app


@click.group()
def celery_group() -> None:
    """Group for celery commands."""
    pass


@celery_group.command()
def run_celery() -> None:
    """Runs the Celery application instance."""
    worker = celery_app.Worker(include=["myndapp.distributed.worker"])
    worker.start()
