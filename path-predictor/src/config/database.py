import os
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_HOST = os.getenv("ANALYTICS_DB_HOST", "localhost")
DB_PORT = int(os.getenv("ANALYTICS_DB_PORT", "5433"))
DB_NAME = os.getenv("ANALYTICS_DB_NAME", "analytics_db")
DB_USER = os.getenv("ANALYTICS_DB_USER", "postgres")
DB_PASSWORD = os.getenv("ANALYTICS_DB_PASSWORD", "postgres")
DATABASE_URL = (
    os.getenv("ANALYTICS_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

_engine: Engine | None = None

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    module_id INTEGER,
    prediction_proba DECIMAL(5,4),
    prediction_class INTEGER,
    model_version VARCHAR(20),
    predicted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    prediction_id INTEGER,
    student_id INTEGER,
    course_id INTEGER,
    severity VARCHAR(10),
    risk_factors JSONB,
    recommended_actions JSONB,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    version VARCHAR(20),
    mlflow_run_id VARCHAR(100),
    stage VARCHAR(20),
    metrics JSONB,
    registered_at TIMESTAMP DEFAULT NOW()
);
"""

FEATURES_QUERY = """
SELECT
    sm.student_id,
    COALESCE(sm.engagement_score, 0) AS engagement_score,
    COALESCE(sm.success_rate, 0) AS success_rate,
    COALESCE(sm.punctuality_score, 0) AS punctuality_score,
    COALESCE(sp.profile_id, 0) AS profile_id,
    COALESCE(tf.engagement_ma30, 0) AS engagement_ma30,
    COALESCE(sm.previous_module_grade, 0) AS previous_module_grade,
    COALESCE(sm.forum_participation, 0) AS forum_participation,
    COALESCE(sm.time_spent_ratio, 0) AS time_spent_ratio,
    COALESCE(sm.absence_days_last_30, 0) AS absence_days_last_30,
    COALESCE(sm.assignment_completion_rate, 0) AS assignment_completion_rate,
    COALESCE(sm.passed, NULL) AS passed,
    COALESCE(sm.course_id, NULL) AS course_id,
    COALESCE(sm.module_id, NULL) AS module_id
FROM student_metrics sm
LEFT JOIN (
    SELECT DISTINCT ON (student_id) student_id, profile_id, assigned_at
    FROM student_profiles
    ORDER BY student_id, assigned_at DESC
) sp ON sp.student_id = sm.student_id
LEFT JOIN temporal_features tf ON tf.student_id = sm.student_id;
"""

FEATURE_COLUMNS: List[str] = [
    "engagement_score",
    "success_rate",
    "punctuality_score",
    "profile_id",
    "engagement_ma30",
    "previous_module_grade",
    "forum_participation",
    "time_spent_ratio",
    "absence_days_last_30",
    "assignment_completion_rate",
]


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    return _engine


def ensure_schema() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_SQL))


def fetch_features() -> List[Dict[str, Any]]:
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text(FEATURES_QUERY)).mappings().all()
    return [dict(r) for r in rows]


def insert_predictions(preds: List[Dict[str, Any]]) -> List[int]:
    ids: List[int] = []
    engine = get_engine()
    with engine.begin() as conn:
        for p in preds:
            row = conn.execute(text(
                """
                INSERT INTO predictions (student_id, course_id, module_id, prediction_proba, prediction_class, model_version)
                VALUES (:student_id, :course_id, :module_id, :prediction_proba, :prediction_class, :model_version)
                RETURNING id
                """
            ), p).first()
            if row:
                ids.append(row[0])
    return ids


def insert_alerts(alerts: List[Dict[str, Any]]) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        for a in alerts:
            conn.execute(text(
                """
                INSERT INTO alerts (prediction_id, student_id, course_id, severity, risk_factors, recommended_actions)
                VALUES (:prediction_id, :student_id, :course_id, :severity, :risk_factors, :recommended_actions)
                """
            ), a)


def register_model(model_name: str, version: str, mlflow_run_id: str, stage: str, metrics: Dict[str, Any]) -> int:
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text(
            """
            INSERT INTO model_registry (model_name, version, mlflow_run_id, stage, metrics)
            VALUES (:model_name, :version, :mlflow_run_id, :stage, :metrics)
            RETURNING id
            """
        ), {
            "model_name": model_name,
            "version": version,
            "mlflow_run_id": mlflow_run_id,
            "stage": stage,
            "metrics": text(":metrics")
        }).first()
    # Fallback: simple insert without RETURNING if needed
    return int(row[0]) if row else 0


def set_model_stage(model_id: int, stage: str) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("UPDATE model_registry SET stage = :stage WHERE id = :id"), {"stage": stage, "id": model_id})


def get_current_model() -> Dict[str, Any]:
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT * FROM model_registry WHERE stage = 'PRODUCTION' ORDER BY registered_at DESC LIMIT 1")).mappings().first()
    return dict(row) if row else {}


def get_alerts(severity: str | None = None) -> List[Dict[str, Any]]:
    engine = get_engine()
    with engine.begin() as conn:
        if severity:
            rows = conn.execute(text("SELECT * FROM alerts WHERE severity = :sev AND status = 'ACTIVE' ORDER BY created_at DESC"), {"sev": severity}).mappings().all()
        else:
            rows = conn.execute(text("SELECT * FROM alerts WHERE status = 'ACTIVE' ORDER BY created_at DESC")).mappings().all()
    return [dict(r) for r in rows]
