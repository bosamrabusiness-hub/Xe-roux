"""Simple in-process async download manager for MVP."""

from __future__ import annotations

import asyncio
import os
import uuid
import threading
from pathlib import Path
from typing import Dict

from . import ytdlp

# Use appropriate temp directory based on OS
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", os.path.join(os.path.expanduser("~"), "Downloads")))
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2"))

_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
_tasks: Dict[str, threading.Thread] = {}
_status: Dict[str, Dict] = {}


def _download_worker(download_id: str, url: str, format_id: str, filename: str | None):
    """Worker that executes a single yt-dlp download."""
    print(f"DEBUG: Starting download worker for {download_id}")  # Debug log

    def progress_callback(percent: float):
        """Update download progress."""
        print(f"DEBUG: Progress callback called with {percent}%")  # Debug log
        _status[download_id]["progress"] = percent
        _status[download_id]["progressPercent"] = round(percent, 1)

    print(f"DEBUG: Starting download for {download_id}")  # Debug log
    _status[download_id] = {"status": "in_progress", "progress": 0, "progressPercent": 0.0}
    try:
        target = DOWNLOAD_DIR / (filename or f"{download_id}.%(ext)s")
        print(f"DEBUG: Starting download for {download_id} to {target}")  # Debug log
        
        # Use the synchronous download_with_progress function
        asyncio.run(ytdlp.download_with_progress(url, format_id, str(target), progress_callback))
        
        print(f"DEBUG: Download completed for {download_id}")  # Debug log
        
        # Find the actual file that was created (yt-dlp replaces %(ext)s with actual extension)
        actual_file = None
        if filename:
            # If custom filename was provided, use it directly
            actual_file = DOWNLOAD_DIR / filename
        else:
            # Find files that start with the download ID
            matching_files = list(DOWNLOAD_DIR.glob(f"{download_id}.*"))
            if matching_files:
                actual_file = matching_files[0]  # Take the first match
            else:
                # Fallback: try to find any recently created file
                import time
                current_time = time.time()
                recent_files = [f for f in DOWNLOAD_DIR.iterdir() 
                              if f.is_file() and (current_time - f.stat().st_mtime) < 60]
                if recent_files:
                    actual_file = recent_files[0]  # Take most recent
        
        if actual_file and actual_file.exists():
            final_file_path = str(actual_file)
            print(f"DEBUG: Found actual file: {final_file_path}")  # Debug log
        else:
            final_file_path = str(target)  # Fallback to original path
            print(f"DEBUG: Could not find actual file, using original path: {final_file_path}")  # Debug log
        
        _status[download_id] = {
            "status": "finished",
            "filePath": final_file_path,
            "fileUrl": None,
            "progress": 100.0,
            "progressPercent": 100.0,
        }

        # Optional S3 upload
        if os.getenv("ENABLE_S3_UPLOAD", "0") == "1":
            from .storage import upload_to_s3  # local import to avoid heavy deps if disabled

            try:
                presigned_url = asyncio.run(upload_to_s3(target))
                _status[download_id]["fileUrl"] = presigned_url
            except Exception as s3_exc:  # pragma: no cover
                _status[download_id]["s3Error"] = str(s3_exc)

    except Exception as exc:  # noqa: BLE001
        print(f"DEBUG: Download failed for {download_id}: {exc}")  # Debug log
        _status[download_id] = {"status": "error", "message": str(exc), "progress": 0, "progressPercent": 0.0}


async def queue_download(url: str, format_id: str, filename: str | None = None):
    """Public API: queue a download and return its ID."""

    download_id = str(uuid.uuid4())
    _status[download_id] = {"status": "queued"}
    
    # Start the download in a background thread
    thread = threading.Thread(
        target=_download_worker,
        args=(download_id, url, format_id, filename)
    )
    thread.daemon = True
    thread.start()
    _tasks[download_id] = thread
    
    return download_id


def get_status(download_id: str) -> Dict:  # noqa: D401
    """Return current status dict for given download ID."""

    return _status.get(download_id, {"status": "not_found"})