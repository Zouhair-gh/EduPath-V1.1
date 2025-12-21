# RecoBuilder

RecoBuilder is the pedagogical recommendation engine for EduPath. It uses PathPredictor alerts and StudentProfiler profiles to suggest relevant learning resources.

## Features
- Index resources with BERT embeddings (`all-MiniLM-L6-v2`)
- FAISS vector search for semantic retrieval
- Personalized recommendations per student with diversity via MMR
- MinIO integration for media storage
- REST API powered by FastAPI
- PostgreSQL schema leveraging pgvector

## Requirements
- Python 3.12+
- PostgreSQL 15+ with `pgvector` extension (`CREATE EXTENSION vector;`)
- MinIO (or S3-compatible)
- Docker (optional)

## Environment
- DB: `ANALYTICS_DB_HOST`, `ANALYTICS_DB_PORT`, `ANALYTICS_DB_NAME`, `ANALYTICS_DB_USER`, `ANALYTICS_DB_PASSWORD`
- MinIO: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`, `MINIO_SECURE`
- Model: `EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`)

## Install & Run (local)
```powershell
cd C:\Users\hp\Desktop\EduPath\reco-builder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:ANALYTICS_DB_HOST="localhost"
$env:ANALYTICS_DB_PORT="5433"
$env:ANALYTICS_DB_NAME="postgres"
$env:ANALYTICS_DB_USER="postgres"
$env:ANALYTICS_DB_PASSWORD="postgres"
uvicorn src.main:app --host 0.0.0.0 --port 8004
```

## Docker
```powershell
cd C:\Users\hp\Desktop\EduPath\reco-builder
docker compose up -d --build
Invoke-WebRequest -Uri http://localhost:8004/health -UseBasicParsing
```

## API
- `GET /api/recommendations/student/{id}?top_n=5`
- `POST /api/recommendations/feedback`
- `GET /api/resources/search?q=...`
- `POST /api/resources/index`
- `GET /api/resources/{id}`
- `GET /api/recommendations/metrics`

## Indexing Scripts
```powershell
python -m src.scripts.index_resources
python -m src.scripts.update_embeddings
```

## Tests
```powershell
pytest -q
```
