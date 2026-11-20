# One Cloud Run service: FastAPI API under /api/v1 plus the static frontend at /.
# Build context is a staging folder holding backend/ and frontend/ side by side
# (scripts/deploy.sh prepares it, because the two live in separate repos).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    FRONTEND_DIR=/app/frontend

WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

RUN useradd --create-home --uid 10001 app && mkdir -p /app/backend/data && chown -R app /app
USER app

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
