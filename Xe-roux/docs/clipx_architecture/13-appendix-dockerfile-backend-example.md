# 13. Appendix: Dockerfile (Backend) Example
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

