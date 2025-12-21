from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .settings import settings


def _dsn(host, port, db, user, pwd):
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"


def get_source_engine() -> Engine:
    return create_engine(_dsn(
        settings.SOURCE_DB_HOST,
        settings.SOURCE_DB_PORT,
        settings.SOURCE_DB_NAME,
        settings.SOURCE_DB_USER,
        settings.SOURCE_DB_PASSWORD,
    ), pool_pre_ping=True)


def get_analytics_engine() -> Engine:
    return create_engine(_dsn(
        settings.ANALYTICS_DB_HOST,
        settings.ANALYTICS_DB_PORT,
        settings.ANALYTICS_DB_NAME,
        settings.ANALYTICS_DB_USER,
        settings.ANALYTICS_DB_PASSWORD,
    ), pool_pre_ping=True)


SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS student_metrics (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    engagement_score DECIMAL(5,2),
    success_rate DECIMAL(5,2),
    punctuality_score DECIMAL(5,2),
    login_count INTEGER,
    total_time_spent INTEGER,
    forum_posts_count INTEGER,
    resources_viewed_count INTEGER,
    activities_completed INTEGER,
    activities_total INTEGER,
    late_submissions INTEGER,
    avg_grade DECIMAL(5,2),
    last_activity_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS temporal_features (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    feature_date DATE,
    engagement_ma7 DECIMAL(5,2),
    engagement_ma30 DECIMAL(5,2),
    grade_ma7 DECIMAL(5,2),
    grade_ma30 DECIMAL(5,2),
    engagement_trend DECIMAL(10,6),
    activity_pattern JSONB,
    anomaly_flags JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_logs (
    id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100),
    run_id VARCHAR(100) UNIQUE,
    status VARCHAR(20),
    records_processed INTEGER,
    records_failed INTEGER,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER
);

CREATE INDEX IF NOT EXISTS idx_student_metrics_student ON student_metrics(student_id);
CREATE INDEX IF NOT EXISTS idx_temporal_features_student_date ON temporal_features(student_id, feature_date);
CREATE INDEX IF NOT EXISTS idx_pipeline_logs_run ON pipeline_logs(run_id);
"""


def ensure_analytics_schema():
    eng = get_analytics_engine()
    with eng.begin() as conn:
        conn.execute(text(SCHEMA_SQL))
    return eng