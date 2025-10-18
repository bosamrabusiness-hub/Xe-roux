# 4. Component Interaction & Data Flow
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
