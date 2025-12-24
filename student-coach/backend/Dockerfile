FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (psycopg2 build deps not needed for binary wheel)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
# Prefer binary wheels to avoid compiling psycopg2 on slim images
RUN pip install --no-cache-dir --only-binary=:all: -r /app/requirements.txt || \
    pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8091

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8091"]
