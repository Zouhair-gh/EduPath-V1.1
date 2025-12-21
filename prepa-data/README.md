# PrepaData

PrepaData cleans, transforms, and aggregates normalized LMS data from LMSConnector into analytics tables for ML microservices (StudentProfiler, PathPredictor).

## Features
- ETL pipeline with pandas/NumPy and scikit-learn normalization
- Engagement, performance, temporal features, anomaly detection
- FastAPI REST endpoints to expose analytics
- Airflow DAGs for scheduled runs (daily at 02:00 UTC)
- Celery task to trigger pipeline asynchronously
- PostgreSQL analytics schema and pipeline logs

## Project Structure
See folders under `prepa-data/`:
- `src/config`: settings, database engine, celery app
- `src/etl`: extractors, transformers, loaders, pipeline
- `src/features`: engagement, performance, temporal, anomalies
- `src/api`: FastAPI routes and schemas
- `dags`: Airflow DAGs (`daily_pipeline.py`, `backfill_pipeline.py`)
- `tests`: unit tests for transformers/features
- `notebooks`: exploratory analysis notebook

## Environment Variables
Key variables (defaults shown):
- SOURCE_DB_HOST/PORT/NAME/USER/PASSWORD (LMSConnector DB, default `edupath`)
- ANALYTICS_DB_HOST/PORT/NAME/USER/PASSWORD (analytics DB)
- API_HOST=`0.0.0.0`, API_PORT=`8001`
- PIPELINE_SCHEDULE=`0 2 * * *`, BATCH_SIZE=`1000`, OUTLIER_THRESHOLD=`3`
- ENGAGEMENT_WEIGHTS=`0.3,0.3,0.2,0.2`
- CELERY_BROKER_URL=`redis://localhost:6379/0`, CELERY_RESULT_BACKEND=`redis://localhost:6379/0`

## Quick Start (Docker Compose)

```bash
cd prepa-data
docker compose up -d --build
```

API runs on `http://localhost:8001`.

## API Endpoints
- GET `/api/health`
- GET `/api/metrics/student/{id}`
- GET `/api/metrics/course/{id}`
- GET `/api/engagement/trends?days=30`
- POST `/api/pipeline/trigger`
- GET `/api/pipeline/status`
- GET `/api/features/temporal/{student_id}`

## Run Locally

```bash
pip install -r requirements.txt
python -m src.main
```

## Tests

```bash
pytest -q
```

## Airflow
Place DAGs under `dags/` in your Airflow instance; with docker compose provided, access the UI at `http://localhost:8080` (user: admin / pass: admin).

## Notes
- Ensure LMSConnector DB is reachable and contains normalized tables (students, courses, enrollments, grades, activity_logs).
- The pipeline logs are stored in `pipeline_logs` for observability.
