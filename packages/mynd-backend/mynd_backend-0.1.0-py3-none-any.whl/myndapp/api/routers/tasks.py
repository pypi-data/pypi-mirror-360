"""Module for the stereo router of the Mynd API."""

from pathlib import Path
from typing import TypeAlias

import celery

from fastapi import APIRouter, HTTPException

from mynd.utils.log import logger

from myndapp.api.dependencies import SessionDep
from myndapp.distributed.worker import celery_app


router = APIRouter()


@router.get("/tasks/info")
async def get_task_info() -> dict:
    """Retrieves information for the spawned Celery tasks."""
    i = celery_app.control.inspect()

    registered_tasks: dict[str, list] | None = i.registered()
    scheduled_tasks: dict[str, list] | None = i.scheduled()
    active_tasks: dict[str, list] | None = i.active()
    reserved_tasks: dict[str, list] | None = i.reserved()

    task_data: dict = dict()
    task_data["registered"] = registered_tasks
    task_data["scheduled"] = scheduled_tasks
    task_data["active"] = active_tasks
    task_data["reserved"] = reserved_tasks

    return task_data


@router.post(
    "/tasks/{task_id}/revoke",
    tags=["tasks"],
)
async def revoke_task(task_id: str) -> None:
    """Revokes a task with the given id."""
    celery.task.control.revoke(task_id, terminate=True)
