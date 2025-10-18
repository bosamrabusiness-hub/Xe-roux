# 6. Deployment Plan (Free-Tier Optimized)
## Frontend (Vercel)
- Repo: `github.com/yourorg/clipx-frontend`
- Branch: `main` auto-deploy
- Env vars in Vercel:
  - `NEXT_PUBLIC_API_BASE_URL` → `https://api.clipx.app` (or Render URL)
- Use Vercel for static generation, CDN caching of assets, and edge performance

## Backend (Render / Railway / Fly.io)
- Dockerfile-based deployment recommended
- Minimal instance with 512MB RAM for MVP
- Env vars:
  - `YT_DLP_OPTIONS` (default args)
  - `MAX_CONCURRENT_DOWNLOADS` (default 2)
  - `TMP_DIR` (path to temporary files)
- Health check endpoint `/healthz` for uptime monitors

## CI/CD (GitHub Actions)
- Workflow: `lint -> unit-tests -> build -> docker build -> deploy`
- Frontend: use Vercel deploy action
- Backend: push Docker image to Render or directly deploy via Render/GitHub integration

---
