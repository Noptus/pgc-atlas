# ── Stage 1: Build frontend ──────────────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci
COPY dashboard/ ./
RUN npm run build

# ── Stage 2: Python API ─────────────────────────────────────────────
FROM python:3.11-slim AS api
WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pgc_explorer/ pgc_explorer/
COPY api/ api/
COPY --from=frontend /app/dashboard/dist /app/static

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
