# 3. High-Level Components
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
