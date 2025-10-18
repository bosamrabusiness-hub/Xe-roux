# 9. Observability & Monitoring
- **Logs:** structured JSON logs emitted to stdout (Render captures logs)
- **Errors:** Sentry for exception tracking (free tier available)
- **Metrics:** Prometheus (self-hosted) or lightweight usage metrics via Umami for frontend
- **Health Checks:** periodic checks via UptimeRobot to `/healthz`
- **Alerts:** email/Slack notifications for error spikes or high latency

---
