# 5. API Specification (Summary)
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
