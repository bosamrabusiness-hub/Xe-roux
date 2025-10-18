"""S3 storage helper for ClipX.

Provides an async-compatible `upload_to_s3` helper that uploads the given file to
an S3 bucket (or compatible service like MinIO / LocalStack) and returns a
presigned download URL valid for a limited time (default: 24 h).

The upload is executed in a background thread so that the FastAPI event loop is
not blocked by the synchronous boto3 client.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Final

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Environment variables (names follow Story 1.05 spec)
S3_ENDPOINT: Final[str | None] = os.getenv("S3_ENDPOINT")
S3_ACCESS_KEY: Final[str | None] = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY: Final[str | None] = os.getenv("S3_SECRET_KEY")
S3_BUCKET_NAME: Final[str | None] = os.getenv("S3_BUCKET")
AWS_REGION: Final[str | None] = os.getenv("AWS_REGION", "us-east-1")
PRESIGN_EXPIRES_SECONDS: Final[int] = int(os.getenv("S3_PRESIGN_TTL", "3600"))  # 1h default

_session = boto3.session.Session()
_s3 = _session.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=boto3.session.Config(s3={'addressing_style': 'path'}),
)
# Disable boto3 logger noise unless explicitly enabled
if os.getenv("S3_DEBUG", "0") != "1":
    import logging
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)


async def upload_to_s3(file_path: str | Path) -> str:  # pragma: no cover
    """Upload *file_path* to ``S3_BUCKET_NAME`` and return a presigned URL.

    The object key will be the filename (no directories). If the bucket/env is
    not configured, raises ``RuntimeError``.
    """

    if not S3_BUCKET_NAME:
        raise RuntimeError("S3_BUCKET_NAME env var is not configured")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)

    key = path.name

    def _upload() -> None:
        _s3.upload_file(str(path), S3_BUCKET_NAME, key)

    # run sync upload in a thread so as not to block
    await asyncio.to_thread(_upload)

    try:
        presigned_url = _s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": key},
            ExpiresIn=PRESIGN_EXPIRES_SECONDS,
        )
    except (ClientError, BotoCoreError) as exc:  # pragma: no cover
        raise RuntimeError(f"Failed to create presigned URL: {exc}") from exc

    return presigned_url