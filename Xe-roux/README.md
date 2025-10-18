<!-- Animated README for Xe-roux -->
<p align="center">
  <img src="assets/banner.svg" alt="Xe-roux Banner" />
</p>

<h1 align="center">🎬 Xe-roux</h1>

<p align="center">
  <strong>Your all-in-one hub for clipping & downloading videos!</strong>
</p>

---

## 🚀 Features

- ✂️ Clip and trim any online video
- ⬇️ Fast downloads in multiple formats & resolutions
- 🔍 Track and view your download history
- ⚡ Async background processing for heavy tasks
- 🌐 Modern React + FastAPI full-stack architecture

## 📸 Demo

> Spin up locally:
>
> ```bash
> # Backend
> uvicorn app.main:app --reload
>
> # Frontend
> cd xe-roux && npm install && npm run dev
> ```
>
> Then visit <http://localhost:5173> to explore Xe-roux.

## 🛠️ Tech Stack

| Layer   | Tech |
|---------|------|
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Backend  | FastAPI + Celery + Redis |
| Storage  | Amazon S3 (or MinIO) |
| CI/CD    | GitHub Actions |

## 🗺️ Project Structure

```
xe-roux/          # Front-end app
app/              # FastAPI backend
redis/            # Local Redis for dev
scripts/          # Helper scripts
```

## 🤝 Contributing

1. Fork the repo and create your branch: `git checkout -b feature/my-feature`
2. Commit your changes: `git commit -m 'Add some feature'`
3. Push to the branch: `git push origin feature/my-feature`
4. Open a Pull Request

## 📄 License

MIT © 2025 Xe-roux
