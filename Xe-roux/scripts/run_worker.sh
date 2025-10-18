#!/usr/bin/env bash
# Simple helper to start a Celery worker for ClipX
# Usage: ./scripts/run_worker.sh [concurrency]

set -euo pipefail

CONCURRENCY="${1:-${CELERY_CONCURRENCY:-2}}"

export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"

exec celery -A app.celery_worker.celery_app worker --loglevel=info -c "$CONCURRENCY"