# 10. Operational Playbooks
## Basic Recovery
1. If backend unresponsive → check instance logs on Render → restart service
2. If `yt-dlp` failing for a platform → add parser update or pin yt-dlp to latest and redeploy
3. If disk fills (tmp) → remove files older than X minutes, scale instance, or move to S3

## Abuse Response
1. Increase rate limits and create temporary block rules for offending IPs
2. Add CAPTCHA on PasteBar if automated abuse suspected
3. Notify stakeholders and consider temporary maintenance mode

---
