import os
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_HOST = os.getenv("ANALYTICS_DB_HOST", "localhost")
DB_PORT = int(os.getenv("ANALYTICS_DB_PORT", "5433"))
DB_NAME = os.getenv("ANALYTICS_DB_NAME", "analytics_db")
DB_USER = os.getenv("ANALYTICS_DB_USER", "postgres")
DB_PASSWORD = os.getenv("ANALYTICS_DB_PASSWORD", "password")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

_engine: Engine | None = None

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS student_profiles (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    profile_id INTEGER,
    profile_label VARCHAR(50),
    confidence_score DECIMAL(5,2),
    assigned_at TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS profile_definitions (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER UNIQUE,
    label VARCHAR(50),
    description TEXT,
    avg_engagement DECIMAL(5,2),
    avg_success_rate DECIMAL(5,2),
    avg_punctuality DECIMAL(5,2),
    student_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clustering_history (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(20) UNIQUE,
    n_clusters INTEGER,
    silhouette_score DECIMAL(5,4),
    inertia DECIMAL(10,2),
    features_used JSONB,
    trained_at TIMESTAMP DEFAULT NOW()
);
"""

FEATURES_QUERY = """
SELECT
    sm.student_id,
    COALESCE(sm.engagement_score, 0) AS engagement_score,
    COALESCE(sm.success_rate, 0) AS success_rate,
    COALESCE(sm.punctuality_score, 0) AS punctuality_score,
    COALESCE(tf.engagement_ma30, 0) AS engagement_ma30,
    COALESCE(sm.login_frequency, 0) AS login_frequency,
    COALESCE(sm.forum_participation, 0) AS forum_participation
FROM student_metrics sm
LEFT JOIN temporal_features tf ON tf.student_id = sm.student_id;
"""

FEATURE_COLUMNS: List[str] = [
    "engagement_score",
    "success_rate",
    "punctuality_score",
    "engagement_ma30",
    "login_frequency",
    "forum_participation",
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


def upsert_student_profiles(assignments: List[Dict[str, Any]]) -> None:
    if not assignments:
        return
    engine = get_engine()
    with engine.begin() as conn:
        for a in assignments:
            conn.execute(
                text(
                    """
                    INSERT INTO student_profiles (student_id, profile_id, profile_label, confidence_score, model_version)
                    VALUES (:student_id, :profile_id, :profile_label, :confidence_score, :model_version)
                    """
                ),
                a,
            )


def upsert_profile_definitions(defs: List[Dict[str, Any]]) -> None:
    if not defs:
        return
    engine = get_engine()
    with engine.begin() as conn:
        for d in defs:
            conn.execute(
                text(
                    """
                    INSERT INTO profile_definitions (profile_id, label, description, avg_engagement, avg_success_rate, avg_punctuality, student_count)
                    VALUES (:profile_id, :label, :description, :avg_engagement, :avg_success_rate, :avg_punctuality, :student_count)
                    ON CONFLICT (profile_id) DO UPDATE SET
                        label = EXCLUDED.label,
                        description = EXCLUDED.description,
                        avg_engagement = EXCLUDED.avg_engagement,
                        avg_success_rate = EXCLUDED.avg_success_rate,
                        avg_punctuality = EXCLUDED.avg_punctuality,
                        student_count = EXCLUDED.student_count
                    """
                ),
                d,
            )


def insert_clustering_history(record: Dict[str, Any]) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO clustering_history (model_version, n_clusters, silhouette_score, inertia, features_used)
                VALUES (:model_version, :n_clusters, :silhouette_score, :inertia, :features_used)
                ON CONFLICT (model_version) DO NOTHING
                """
            ),
            record,
        )


def latest_metrics() -> Dict[str, Any]:
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT * FROM clustering_history ORDER BY trained_at DESC LIMIT 1")).mappings().first()
    return dict(row) if row else {}
