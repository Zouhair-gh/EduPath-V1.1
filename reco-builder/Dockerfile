FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_PORT=8004 \
    ANALYTICS_DB_HOST=host.docker.internal \
    ANALYTICS_DB_PORT=5433 \
    ANALYTICS_DB_NAME=postgres \
    ANALYTICS_DB_USER=postgres \
    ANALYTICS_DB_PASSWORD=postgres \
    EMBEDDING_MODEL=all-MiniLM-L6-v2 \
    MINIO_ENDPOINT=host.docker.internal:9000 \
    MINIO_ACCESS_KEY=minioadmin \
    MINIO_SECRET_KEY=minioadmin \
    MINIO_BUCKET=educational-resources \
    MINIO_SECURE=False

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY indexes ./indexes
COPY models ./models

EXPOSE 8004
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"]