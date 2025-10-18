# 7. Scalability & Operational Patterns
## Short-term (MVP)
- Single backend instance, process downloads directly with async subprocess calls
- Limit concurrency: `MAX_CONCURRENT_DOWNLOADS = 2`
- Enforce per-IP rate-limits at backend using `fastapi-limiter` + Redis (or in-memory token bucket)
- Cleanup policy: delete files older than 5 minutes or post-download

## Medium-term
- Add Celery workers + Redis to offload long-running downloads and scale horizontally
- Move temporary files to S3/Spaces and serve via pre-signed URLs
- Autoscaling on backend instances (if using paid infra)

## Long-term
- Use Kubernetes + Horizontal Pod Autoscaler with persistent shared storage
- Implement multi-region distribution and CDN for serving large files

---
