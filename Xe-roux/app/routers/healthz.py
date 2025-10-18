from fastapi import APIRouter, status

router = APIRouter()

# Import celery with fallback
try:
    from app.celery_worker import celery_app
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    celery_app = None

import redis
import os

# Import boto3 with fallback
try:
    import boto3
    import botocore
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    botocore = None


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
S3_ENABLED = os.getenv("ENABLE_S3_UPLOAD", "0") == "1"
S3_BUCKET = os.getenv("S3_BUCKET")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")


@router.get("/healthz", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Health endpoint that verifies Redis (broker) connectivity."""
    try:
        # Lightweight ping to Redis to ensure it's reachable
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()
        broker_ok = True
    except Exception:  # noqa: BLE001
        broker_ok = False

    try:
        if S3_ENABLED and BOTO3_AVAILABLE:
            s3 = boto3.client("s3", endpoint_url=S3_ENDPOINT)
            # attempt list bucket to verify perms
            s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=1)
            s3_ok = True
        else:
            s3_ok = None if not S3_ENABLED else False
    except Exception:
        s3_ok = False

    return {
        "status": "ok" if broker_ok and (s3_ok in (True, None)) else "degraded",
        "redis": "reachable" if broker_ok else "unreachable",
        "s3": "ok" if s3_ok else ("disabled" if s3_ok is None else "unreachable"),
    }