import pandas as pd
from sqlalchemy import text
from ..config.database import get_analytics_engine, ensure_analytics_schema
from ..utils.logger import logger


def write_student_metrics(df: pd.DataFrame):
    ensure_analytics_schema()
    eng = get_analytics_engine()
    logger.info(f"Loading student metrics: {len(df)} rows")
    df.to_sql('student_metrics', eng, if_exists='append', index=False)


def write_temporal_features(df: pd.DataFrame):
    ensure_analytics_schema()
    eng = get_analytics_engine()
    logger.info(f"Loading temporal features: {len(df)} rows")
    df.to_sql('temporal_features', eng, if_exists='append', index=False)


def log_pipeline(run_id: str, status: str, processed: int, failed: int, error_message: str = None):
    ensure_analytics_schema()
    eng = get_analytics_engine()
    with eng.begin() as conn:
        conn.execute(text(
            "INSERT INTO pipeline_logs(pipeline_name, run_id, status, records_processed, records_failed, error_message, started_at, completed_at, duration_seconds) "
            "VALUES(:pipeline_name, :run_id, :status, :processed, :failed, :error_message, NOW(), NOW(), 0)"),
            {
                'pipeline_name': 'daily_prepa_data_pipeline',
                'run_id': run_id,
                'status': status,
                'processed': processed,
                'failed': failed,
                'error_message': error_message or ''
            }
        )