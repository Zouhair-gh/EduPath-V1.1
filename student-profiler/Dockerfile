# StudentProfiler Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    API_PORT=8002 \
    N_CLUSTERS=5 \
    PCA_COMPONENTS=2 \
    MODEL_VERSION=v1.0 \
    ANALYTICS_DB_HOST=host.docker.internal \
    ANALYTICS_DB_PORT=5433 \
    ANALYTICS_DB_NAME=analytics_db \
    ANALYTICS_DB_USER=postgres \
    ANALYTICS_DB_PASSWORD=postgres

WORKDIR /app

# System deps (optional, kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
RUN mkdir -p models

EXPOSE 8002

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002"]
