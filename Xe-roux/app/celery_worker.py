"""Celery application and tasks for ClipX backend.

This module defines the Celery application instance as ``celery_app`` so it can be
imported by other modules (e.g. FastAPI routers) and by the Celery worker
process itself.  Tasks are autodiscovered from the ``app`` package, but we also
explicitly register the main download task here for clarity.

Running a worker locally:

    celery -A app.celery_worker.celery_app worker --loglevel=info

The broker/result backend URLs are taken from the ``REDIS_URL`` environment
variable.  When not set we fall back to the local default
``redis://localhost:6379/0`` which works seamlessly with the Docker Compose
setup introduced in Story 1.03.
"""
from __future__ import annotations

import os
import asyncio
import uuid
from pathlib import Path
from typing import Any, Dict

from celery import Celery, states
from celery.signals import after_setup_task_logger

# ---------------------------------------------------------------------------
# Celery application setup
# ---------------------------------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "clipx",  # name of celery app
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.celery_worker"],  # ensure this module is always imported
)

# Optional configuration – keep things minimal for now
celery_app.conf.task_track_started = True
celery_app.conf.broker_connection_retry_on_startup = True

DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/tmp"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
async def _run_ytdlp(url: str, format_id: str, filepath: Path) -> None:
    """Run yt-dlp asynchronously to download the requested video.

    We use the existing helper in :pymod:`app.services.ytdlp` so the logic is
    shared with the in-process downloader that was part of Story 1.02.
    """
    from app.services import ytdlp  # local import to avoid celery serialization issues

    cmd = [
        "yt-dlp",
        "-f",
        format_id,
        "-o",
        str(filepath),
        url,
    ]
    await ytdlp._run_cmd(cmd)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
@celery_app.task(bind=True, name="download_video", track_started=True)
def download_video_task(self, url: str, format_id: str, filename: str | None = None) -> Dict[str, Any]:
    """Celery task that downloads a video using yt-dlp.

    Progress updates are pushed to the task meta via ``self.update_state`` so
    they can be queried through the status endpoint.
    """
    # Generate deterministic filename if not provided
    download_id = self.request.id or str(uuid.uuid4())
    target_name = filename or f"{download_id}.%(ext)s"
    target_path = DOWNLOAD_DIR / target_name

    try:
        # Run the yt-dlp command inside an event loop – Celery tasks are sync so we
        # manually drive the async function.
        asyncio.run(_run_ytdlp(url, format_id, target_path))

        result = {
            "status": "finished",
            "filePath": str(target_path),
        }
        return result
    except Exception as exc:  # noqa: BLE001
        # Mark task as failed and include the error message in meta for clients.
        self.update_state(
            state=states.FAILURE,
            meta={
                "status": "error",
                "message": str(exc),
            },
        )
        # Re-raise so Celery records the traceback
        raise


# ---------------------------------------------------------------------------
# Logging tweaks
# ---------------------------------------------------------------------------
@after_setup_task_logger.connect
def _configure_task_logger(logger, *args, **kwargs):  # noqa: D401, ANN001
    """Tweak Celery task log format for readability."""
    for handler in logger.handlers:
        handler.setFormatter(
            handler.formatter.__class__(
                "% (levelname)s | %(name)s | %(message)s"
            )
        )