"""Main FastAPI application factory for ClipX backend MVP."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# Import FastAPILimiter with fallback
try:
    from fastapi_limiter import FastAPILimiter
    from redis import asyncio as aioredis
except ImportError:
    # Create dummy FastAPILimiter for fallback
    class FastAPILimiter:
        _disabled = True
        @classmethod
        def init(cls, *args, **kwargs):
            pass
# Simplified imports for Windows compatibility
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from app.cleanup import periodic_cleanup
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
from app.routers import download, healthz, preview

# Configuration via environment variables
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global scheduler instance (shared across app lifespan)
scheduler = AsyncIOScheduler() if SCHEDULER_AVAILABLE else None


async def _init_rate_limiter() -> None:  # pragma: no cover
    """Initialize FastAPI-Limiter using Redis backend.

    If Redis is not reachable, the application will still start but the
    rate-limiting dependencies will degrade to no-op stubs so that routes
    depending on ``RateLimiter`` continue to work without raising 500 errors.
    """
    # Check if fastapi_limiter is available
    if not hasattr(FastAPILimiter, '_disabled'):
        try:
            redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
            # Proactively check connectivity – if Redis is down this will raise
            await redis.ping()
            await FastAPILimiter.init(redis)
        except Exception as exc:  # noqa: BLE001
            # Redis unavailable – fallback to dummy limiter so that the app can start
            import logging
            from fastapi import Depends  # local import to avoid circular
            
            try:
                import fastapi_limiter.depends as _depends
                
                logging.warning("Rate limiter disabled – Redis unreachable: %s", exc)

                async def _dummy_dep():  # pragma: no cover
                    return  # just allow the request to proceed

                # Replace RateLimiter dependency factory with a no-op variant
                old_rl = _depends.RateLimiter
                _depends.RateLimiter = lambda *a, **kw: Depends(_dummy_dep)

                # Also patch existing RateLimiter instances to become no-ops
                async def _no_op_rate_limiter(self, request, response=None):  # type: ignore[unused-argument]
                    return  # simply allow
                # Monkeypatch __call__ on original class so already-created instances work
                old_rl.__call__ = _no_op_rate_limiter  # type: ignore[assignment]

                # Propagate the patched RateLimiter to any modules that already imported it
                import sys, inspect
                for module in list(sys.modules.values()):
                    if module is None:
                        continue
                    rl_attr = getattr(module, "RateLimiter", None)
                    if rl_attr is old_rl:
                        setattr(module, "RateLimiter", _depends.RateLimiter)

                # Also mark limiter as disabled for other checks
                setattr(FastAPILimiter, "_disabled", True)
            except ImportError:
                # fastapi_limiter not available at all
                logging.warning("Rate limiter disabled – fastapi_limiter not available: %s", exc)
                setattr(FastAPILimiter, "_disabled", True)
    else:
        # fastapi_limiter not available at all
        import logging
        logging.warning("Rate limiter disabled – fastapi_limiter not available")


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""

    app = FastAPI(title="ClipX Backend MVP", version="1.0.0")

    # Allow all origins (tighten for production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup tasks
    @app.on_event("startup")
    async def on_startup() -> None:  # noqa: D401
        await _init_rate_limiter()
        if scheduler:
            scheduler.start()
            scheduler.add_job(periodic_cleanup, "interval", minutes=30)
        # Fallback cleanup loop for environments where APScheduler is disabled
        if SCHEDULER_AVAILABLE:
            app.state.cleanup_task = asyncio.create_task(periodic_cleanup())

    # Shutdown tasks
    @app.on_event("shutdown")
    async def on_shutdown() -> None:  # noqa: D401
        if scheduler:
            scheduler.shutdown(wait=False)
        cleanup_task: asyncio.Task | None = getattr(app.state, "cleanup_task", None)
        if cleanup_task:
            cleanup_task.cancel()

    # Custom handler for 429 Too Many Requests
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):  # type: ignore[override]
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail or "Rate limit exceeded. Try again later."},
                headers={"Retry-After": exc.headers.get("Retry-After", "60")} if exc.headers else {},
            )
        raise exc

    # Routers
    app.include_router(healthz.router)
    app.include_router(preview.router, prefix="/preview", tags=["preview"])
    app.include_router(download.router, prefix="/download", tags=["download"])

    return app


app = create_app()