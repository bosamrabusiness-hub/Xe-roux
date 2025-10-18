from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
import os
from fastapi.responses import FileResponse
from pathlib import Path

# Try to import Celery, fallback to local processing if Redis unavailable
try:
    import os
    import redis
    # Test Redis connection first before importing Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(REDIS_URL, socket_connect_timeout=1)
    redis_client.ping()
    # If Redis is reachable, import Celery
    from app.celery_worker import celery_app
    CELERY_AVAILABLE = True
except Exception:
    CELERY_AVAILABLE = False
    # Import the in-process downloader for fallback
    from app.services.downloader import queue_download, get_status

# Import RateLimiter with fallback
try:
    from fastapi_limiter.depends import RateLimiter
    from fastapi import Depends
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    # Create dummy RateLimiter for fallback
    RATE_LIMITER_AVAILABLE = False
    def RateLimiter(times=None, seconds=None):  # noqa: N802
        class DummyRateLimiter:
            def __init__(self, times=None, seconds=None):
                self.times = times
                self.seconds = seconds
            
            async def __call__(self):
                pass
        return DummyRateLimiter(times, seconds)

from utils.validators import validate_url

router = APIRouter()


class DownloadRequest(BaseModel):
    url: str
    format: str | None = "best"
    resolution: str | None = None
    filename: str | None = None


rate_limiter_dep = RateLimiter(times=3, seconds=1800) if RATE_LIMITER_AVAILABLE else None

@router.post("/", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(rate_limiter_dep)] if rate_limiter_dep else [])
async def download_video(payload: DownloadRequest):
    """Enqueue a download task and return the task ID."""
    url = validate_url(payload.url)
    
    if not CELERY_AVAILABLE:
        # Fallback: Use in-process downloader
        try:
            download_id = await queue_download(url, payload.format or "best", payload.filename)
            return {"downloadId": download_id, "status": "queued", "note": "Using in-process downloader"}
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Download failed: {str(exc)}") from exc
    
    try:
        task = celery_app.send_task(
            "download_video",
            args=[url, payload.format, payload.filename],
        )
        return {"downloadId": task.id, "status": "queued"}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status/{download_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter())] if RATE_LIMITER_AVAILABLE else [])
async def download_status(download_id: str):
    """Return download task status and meta info."""
    if not CELERY_AVAILABLE:
        # Fallback: Use in-process downloader status
        status_info = get_status(download_id)
        if status_info.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Download not found")
        
        # Map status to Celery-like format
        state_mapping = {
            "queued": "PENDING",
            "in_progress": "STARTED",
            "finished": "SUCCESS",
            "error": "FAILURE"
        }
        
        return {
            "downloadId": download_id,
            "state": state_mapping.get(status_info.get("status", "queued"), "PENDING"),
            "info": status_info
        }
    
    async_result = celery_app.AsyncResult(download_id)
    response = {
        "downloadId": download_id,
        "state": async_result.state,
        "info": async_result.info,
    }
    return response


@router.get("/file/{download_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter())] if RATE_LIMITER_AVAILABLE else [])
async def download_file(download_id: str):
    """Serve the downloaded file directly to the user's device."""
    if not CELERY_AVAILABLE:
        # Fallback: Use in-process downloader status
        status_info = get_status(download_id)
        if status_info.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Download not found")
        
        if status_info.get("status") != "finished":
            raise HTTPException(status_code=400, detail="Download not yet complete")
        
        file_path = status_info.get("filePath")
        if not file_path or not Path(file_path).exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get the actual filename from the path
        file_name = Path(file_path).name
        
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/octet-stream"
        )
    
    # For Celery-based downloads, we would need to check the task result
    # This is a placeholder for the Celery implementation
    async_result = celery_app.AsyncResult(download_id)
    if async_result.state != "SUCCESS":
        raise HTTPException(status_code=400, detail="Download not yet complete")
    
    # Extract file path from task result
    file_path = async_result.result.get("file_path") if async_result.result else None
    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_name = Path(file_path).name
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream"
    )