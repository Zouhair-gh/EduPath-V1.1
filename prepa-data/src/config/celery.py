from celery import Celery
from .settings import settings

celery_app = Celery(
    'prepa_data',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

@celery_app.task(name='prepa_data.run_pipeline')
def run_pipeline_task():
    from ..etl.pipeline import run_pipeline_once
    return run_pipeline_once()
