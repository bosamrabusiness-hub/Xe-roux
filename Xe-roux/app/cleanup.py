"""Background task to periodically clean up old files in /tmp.

Uses asyncio.sleep loop. Can be used in FastAPI lifespan or Celery beat.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Final

DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/tmp"))
TTL_MINUTES: Final[int] = int(os.getenv("TEMP_FILE_TTL_MINUTES", "10"))
CHECK_INTERVAL_SECONDS: Final[int] = 300  # every 5 min


async def _remove_old_files() -> None:  # pragma: no cover
    cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=TTL_MINUTES)
    for file in DOWNLOAD_DIR.glob("*"):
        if not file.is_file():
            continue
        mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            try:
                file.unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                pass


async def periodic_cleanup() -> None:  # pragma: no cover
    while True:
        await _remove_old_files()
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)