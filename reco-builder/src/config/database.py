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

SCHEMA_RESOURCES_SQL = """
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    resource_type VARCHAR(50),
    subject VARCHAR(100),
    difficulty_level VARCHAR(20),
    duration_minutes INTEGER,
    url VARCHAR(500),
    minio_key VARCHAR(255),
    tags JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

SCHEMA_EMBEDDINGS_SQL = """
CREATE TABLE IF NOT EXISTS resource_embeddings (
    id SERIAL PRIMARY KEY,
    resource_id INTEGER REFERENCES resources(id) ON DELETE CASCADE,
    embedding_model VARCHAR(100),
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);
"""

SCHEMA_RECO_SQL = """
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    student_id INTEGER,
    resource_id INTEGER REFERENCES resources(id),
    recommendation_score DECIMAL(5,4),
    context JSONB,
    recommended_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations(id) ON DELETE CASCADE,
    student_id INTEGER,
    action VARCHAR(20),
    time_spent_seconds INTEGER,
    feedback_at TIMESTAMP DEFAULT NOW()
);
"""


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3}
        )
    return _engine


def ensure_schema() -> None:
    engine = get_engine()
    # Attempt to enable pgvector extension, but don't block
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    except Exception as e:
        print(f"[WARN] pgvector not available: {e}")
    # Create core tables regardless
    try:
        with engine.begin() as conn:
            conn.execute(text(SCHEMA_RESOURCES_SQL))
            conn.execute(text(SCHEMA_RECO_SQL))
    except Exception as e:
        print(f"[WARN] core tables creation issue: {e}")
    # Create embeddings table and index if pgvector exists
    try:
        with engine.begin() as conn:
            conn.execute(text(SCHEMA_EMBEDDINGS_SQL))
            conn.execute(text("CREATE INDEX IF NOT EXISTS resource_embeddings_ivfflat ON resource_embeddings USING ivfflat (embedding vector_cosine_ops);"))
    except Exception as e:
        print(f"[WARN] embeddings table/index skipped: {e}")


def fetch_resources() -> List[Dict[str, Any]]:
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM resources ORDER BY created_at DESC")).mappings().all()
    return [dict(r) for r in rows]


def fetch_embeddings() -> List[Dict[str, Any]]:
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT resource_id, embedding FROM resource_embeddings ORDER BY resource_id"))
        result: List[Dict[str, Any]] = []
        for rid, emb in rows:
            # emb is a vector type; pgvector returns list-like via psycopg
            result.append({"resource_id": int(rid), "embedding": emb})
    return result


def upsert_embedding(resource_id: int, embedding: List[float], model: str) -> None:
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(text(
                """
                INSERT INTO resource_embeddings (resource_id, embedding_model, embedding)
                VALUES (:rid, :model, :embedding)
                ON CONFLICT (resource_id) DO UPDATE SET embedding = EXCLUDED.embedding, embedding_model = EXCLUDED.embedding_model
                """
            ), {"rid": resource_id, "model": model, "embedding": embedding})
    except Exception as e:
        print(f"[WARN] upsert_embedding skipped for resource {resource_id}: {e}")


def log_recommendations(student_id: int, recos: List[Dict[str, Any]], context: Dict[str, Any]) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        for r in recos:
            conn.execute(text(
                """
                INSERT INTO recommendations (student_id, resource_id, recommendation_score, context)
                VALUES (:sid, :rid, :score, :ctx)
                """
            ), {"sid": student_id, "rid": r["resource_id"], "score": r["score"], "ctx": context})


def insert_feedback(recommendation_id: int, student_id: int, action: str, time_spent_seconds: int | None) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(
            """
            INSERT INTO recommendation_feedback (recommendation_id, student_id, action, time_spent_seconds)
            VALUES (:rec_id, :sid, :action, :time)
            """
        ), {"rec_id": recommendation_id, "sid": student_id, "action": action, "time": time_spent_seconds})


def recently_viewed(student_id: int, resource_id: int, days: int = 7) -> bool:
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text(
            """
            SELECT 1 FROM recommendation_feedback
            WHERE student_id = :sid AND recommendation_id IN (
                SELECT id FROM recommendations WHERE resource_id = :rid AND student_id = :sid AND recommended_at >= NOW() - INTERVAL ':days days'
            )
            AND action IN ('clicked','completed','liked')
            LIMIT 1
            """
        ), {"sid": student_id, "rid": resource_id, "days": days}).first()
    return bool(row)


def get_student_profile(student_id: int) -> Dict[str, Any]:
    engine = get_engine()
    with engine.begin() as conn:
        # Try to join StudentProfiler tables; fallback to a default
        row = conn.execute(text(
            """
            SELECT sp.profile_id, pd.label, COALESCE(pd.suggested_level,'intermediate') AS suggested_level
            FROM student_profiles sp
            LEFT JOIN profile_definitions pd ON pd.profile_id = sp.profile_id
            WHERE sp.student_id = :sid
            ORDER BY sp.assigned_at DESC
            LIMIT 1
            """
        ), {"sid": student_id}).mappings().first()
    if row:
        return dict(row)
    return {"profile_id": None, "label": "general learner", "suggested_level": "intermediate"}


def get_student_difficulties(student_id: int) -> List[str]:
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text(
            """
            SELECT severity, risk_factors
            FROM alerts
            WHERE student_id = :sid AND status = 'ACTIVE'
            ORDER BY created_at DESC
            LIMIT 5
            """
        ), {"sid": student_id}).mappings().all()
    diffs: List[str] = []
    for r in rows:
        rf = r.get("risk_factors")
        if isinstance(rf, dict):
            diffs.extend([str(k).replace('_',' ') for k in list(rf.keys())[:3]])
    return diffs or ["learning difficulties", "fundamentals", "practice"]
