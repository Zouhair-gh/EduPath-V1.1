FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_PORT=8003 \
    MLFLOW_EXPERIMENT_NAME=path_predictor \
    ALERT_THRESHOLD_HIGH=0.70 \
    ALERT_THRESHOLD_MEDIUM=0.50 \
    ANALYTICS_DB_HOST=host.docker.internal \
    ANALYTICS_DB_PORT=5433 \
    ANALYTICS_DB_NAME=analytics_db \
    ANALYTICS_DB_USER=postgres \
    ANALYTICS_DB_PASSWORD=postgres

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8003
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003", "--log-level", "debug"]
