from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from app.services import ytdlp
from utils.validators import validate_url
from fastapi import Depends

# Import RateLimiter with fallback
try:
    from fastapi_limiter.depends import RateLimiter
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    RATE_LIMITER_AVAILABLE = False
    def RateLimiter(times=None, seconds=None):  # noqa: N802
        class DummyRateLimiter:
            def __init__(self, times=None, seconds=None):
                self.times = times
                self.seconds = seconds
            
            async def __call__(self):
                pass
        return DummyRateLimiter(times, seconds)

router = APIRouter()


class PreviewRequest(BaseModel):
    url: str


@router.post("/", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter())] if RATE_LIMITER_AVAILABLE else [])
async def preview_video(payload: PreviewRequest):
    url = validate_url(payload.url)
    try:
        return await ytdlp.fetch_preview(url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))