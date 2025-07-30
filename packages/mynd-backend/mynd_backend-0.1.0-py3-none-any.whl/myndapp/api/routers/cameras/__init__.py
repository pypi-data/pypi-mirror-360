"""Package for camera router functionality."""

from .camera_base import router as router
from .camera_tasks import (
    assimilate_camera_references,
    assimilate_camera_references_batch,
)

__all__ = []
