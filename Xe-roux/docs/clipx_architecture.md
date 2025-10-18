🏗️ **System Architecture Document — ClipX**

---

## Meta
**Document:** System Architecture
**Project:** ClipX
**Author:** Dr. Ray (Architect)
**Version:** 1.0
**Date:** 16 Oct 2025

---

## 1. Purpose
This document defines the technical architecture for ClipX — a free public web application that lets users download videos/playlists from multiple platforms. It covers system components, data flows, APIs, deployment targets (free-tier optimized), scaling considerations, security, monitoring, and operational playbooks.

---

## 2. Architectural Goals
- **Reliability:** provide stable downloads within free-tier constraints
- **Simplicity:** easy to deploy and maintain (Docker + minimal infra)
- **Cost-efficiency:** operate on zero/low-cost hosting (Vercel + Render/Railway)
- **Extensibility:** allow components to be swapped (e.g., move to paid infra) without major rewrites
- **Security & Legal Awareness:** avoid storing copyrighted content long-term, enforce rate limits, sanitize inputs

---

## 3. High-Level Components
1. **Client (Frontend)**
   - Next.js app hosted on Vercel (static/SSR pages)
   - Responsible for PasteBar UI, PreviewCard, Queue UI, History (localStorage), and invoking API endpoints
2. **API Gateway / Proxy**
   - Next.js API routes (optional) or direct calls from client to Backend
   - Provides small proxy functionality (CORS, API key masking, environment routing)
3. **Backend Service (Download Engine)**
   - FastAPI (Python) service running yt-dlp to fetch video/playlist content, produce metadata and stream files
   - Runs as a Docker container on Render / Railway / Fly.io
4. **Task Queue (Optional for scaling)**
   - Celery (Python) with Redis (hosted free tier) for background jobs (long-running downloads, playlist batches)
   - Alternatively, simple in-process async workers for MVP
5. **Temporary File Storage**
   - Local ephemeral `/tmp` on backend instance (auto-cleanup) for zero-cost deployment
   - Optionally upload to S3/DigitalOcean Spaces for high scale
6. **Database (Optional)**
   - SQLite for basic needs or Supabase (free tier) for future user history and analytics
7. **Monitoring & Logging**
   - Structured logs (stdout to Render logs), optional Sentry for error tracking (free tier)
   - UptimeRobot for health checks
8. **CI/CD**
   - GitHub Actions to build/test and deploy frontend to Vercel and backend to Render

---

## 4. Component Interaction & Data Flow
**Flow: Paste → Preview → Download**
1. User pastes URL in the browser (Next.js client)
2. Client calls `POST /api/preview` (Next.js API route or backend endpoint)
3. API Gateway forwards to FastAPI `POST /preview` → FastAPI calls `yt-dlp` to fetch metadata (no full download), returns title, thumbnail, available formats
4. Client displays PreviewCard and user selects format & quality
5. Client calls `POST /api/download` → Gateway enqueues job to backend
   - If using Celery: job is queued; worker executes yt-dlp to fetch and prepare file into `/tmp`
   - If no queue: FastAPI executes job asynchronously up to configured timeout
6. Backend updates status via polling endpoint `GET /api/download/status/:id` or WebSocket push
7. When file is ready, backend streams or serves file URL to client (signed short-lived URL) and deletes local file after delivery

Diagram (text):
```
Client (Next.js) --HTTPS--> Vercel CDN/Frontend
    └--POST /api/*--> Next.js API (proxy) OR direct --> FastAPI Backend (Render)
FastAPI -- spawns --> yt-dlp process --> writes /tmp/file
FastAPI --> optional upload to S3 or serve directly
Client polls status or listens via websocket -> receives final download URL
```

---

## 5. API Specification (Summary)
**POST /api/preview**
- Request: `{ "url": "https://..." }`
- Response: `{ status, data: { title, thumbnail, duration, formats: [...] } }`

**POST /api/download**
- Request: `{ "url", "format", "resolution", "filename?" }`
- Response: `{ status: 'queued'|'processing', downloadId }`

**GET /api/download/status/:id**
- Response: `{ status, progress, speed, fileUrl?, message? }`

**POST /api/download/cancel**
- Request: `{ downloadId }` → Response: `{ status: 'cancelled' }`

**Security headers:** require `Origin` and implement CORS whitelist; if proxying via Next.js API routes, hide backend URL from public.

---

## 6. Deployment Plan (Free-Tier Optimized)
### Frontend (Vercel)
- Repo: `github.com/yourorg/clipx-frontend`
- Branch: `main` auto-deploy
- Env vars in Vercel:
  - `NEXT_PUBLIC_API_BASE_URL` → `https://api.clipx.app` (or Render URL)
- Use Vercel for static generation, CDN caching of assets, and edge performance

### Backend (Render / Railway / Fly.io)
- Dockerfile-based deployment recommended
- Minimal instance with 512MB RAM for MVP
- Env vars:
  - `YT_DLP_OPTIONS` (default args)
  - `MAX_CONCURRENT_DOWNLOADS` (default 2)
  - `TMP_DIR` (path to temporary files)
- Health check endpoint `/healthz` for uptime monitors

### CI/CD (GitHub Actions)
- Workflow: `lint -> unit-tests -> build -> docker build -> deploy`
- Frontend: use Vercel deploy action
- Backend: push Docker image to Render or directly deploy via Render/GitHub integration

---

## 7. Scalability & Operational Patterns
### Short-term (MVP)
- Single backend instance, process downloads directly with async subprocess calls
- Limit concurrency: `MAX_CONCURRENT_DOWNLOADS = 2`
- Enforce per-IP rate-limits at backend using `fastapi-limiter` + Redis (or in-memory token bucket)
- Cleanup policy: delete files older than 5 minutes or post-download

### Medium-term
- Add Celery workers + Redis to offload long-running downloads and scale horizontally
- Move temporary files to S3/Spaces and serve via pre-signed URLs
- Autoscaling on backend instances (if using paid infra)

### Long-term
- Use Kubernetes + Horizontal Pod Autoscaler with persistent shared storage
- Implement multi-region distribution and CDN for serving large files

---

## 8. Security, Abuse Prevention & Legal Considerations
### Security
- Validate and sanitize all incoming URLs (reject suspicious schemes or local addresses)
- Run `yt-dlp` in a sandboxed environment (Docker) to reduce risk
- Limit size of downloads and reject extremely large files
- Use HTTPS everywhere; set secure cookies and CSP headers
- Protect backend with rate-limiting and CAPTCHAs for suspicious behavior

### Abuse Prevention
- Rate-limit per IP and per API key (if implemented)
- Request throttling and job queue quotas
- Monitor for repeated requests to same target and apply temporary blocks

### Legal Considerations
- Provide clear Terms of Service and a copyright/disclaimer page describing user responsibility
- Do NOT offer built-in redistribution or hosting of copyrighted content; delete temporary files promptly
- Consider geofencing or legal counsel if you plan to expand into monetized operations

---

## 9. Observability & Monitoring
- **Logs:** structured JSON logs emitted to stdout (Render captures logs)
- **Errors:** Sentry for exception tracking (free tier available)
- **Metrics:** Prometheus (self-hosted) or lightweight usage metrics via Umami for frontend
- **Health Checks:** periodic checks via UptimeRobot to `/healthz`
- **Alerts:** email/Slack notifications for error spikes or high latency

---

## 10. Operational Playbooks
### Basic Recovery
1. If backend unresponsive → check instance logs on Render → restart service
2. If `yt-dlp` failing for a platform → add parser update or pin yt-dlp to latest and redeploy
3. If disk fills (tmp) → remove files older than X minutes, scale instance, or move to S3

### Abuse Response
1. Increase rate limits and create temporary block rules for offending IPs
2. Add CAPTCHA on PasteBar if automated abuse suspected
3. Notify stakeholders and consider temporary maintenance mode

---

## 11. Cost Estimate (Free-Friendly)
- **Frontend:** Vercel Free (should be free for our static app)  
- **Backend:** Render/Railway free tier — limited compute (may require occasional upgrades if usage grows)  
- **Redis (optional):** free hosted tiers exist (limited)  
- **Sentry/Monitoring:** free tiers available  
- **Total:** $0–$20/month initially if usage remains low; plan to accept donations if costs increase

---

## 12. Roadmap & Migration Paths
- **If usage grows:** migrate backend to Docker on DigitalOcean Droplet or AWS ECS with S3 for storage
- **For high-scale:** use Kubernetes + managed Redis + CDN + presigned S3 URLs
- **For reliability:** add multi-region failover and autoscaling

---

## 13. Appendix: Dockerfile (Backend) Example
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install --upgrade pip && pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev
COPY . /app
ENV TMP_DIR=/tmp
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

If you want, next I can:
1. Draw a **visual architecture diagram** (SVG/ASCII) and add it to this canvas.  
2. Generate a full **terraform** or **docker-compose** setup for quick local dev and a production-ready `docker-compose` for small-scale hosting.  
3. Produce a detailed **runbook** for daily ops (cleanup, upgrades, logs).

Which should I do next?

