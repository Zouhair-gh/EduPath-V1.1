from fastapi import APIRouter
from sqlalchemy import text
from ..config.database import get_analytics_engine
from ..etl.pipeline import run_pipeline_once

router = APIRouter(prefix="/api")

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/metrics/student/{student_id}")
async def get_student_metrics(student_id: int):
    eng = get_analytics_engine()
    with eng.connect() as conn:
        rows = conn.execute(text("SELECT * FROM student_metrics WHERE student_id=:sid ORDER BY updated_at DESC"), {"sid": student_id}).mappings().all()
        return [dict(r) for r in rows]

@router.get("/metrics/course/{course_id}")
async def get_course_metrics(course_id: int):
    eng = get_analytics_engine()
    with eng.connect() as conn:
        rows = conn.execute(text(
            """
            SELECT
              course_id,
              COUNT(DISTINCT student_id) AS total_students,
              AVG(engagement_score) AS avg_engagement,
              AVG(success_rate)   AS avg_success_rate
            FROM student_metrics
            WHERE course_id = :cid
            GROUP BY course_id
            """
        ), {"cid": course_id}).mappings().all()
        return [dict(r) for r in rows]

@router.get("/engagement/trends")
async def engagement_trends(days: int = 30):
    eng = get_analytics_engine()
    with eng.connect() as conn:
        rows = conn.execute(text("SELECT student_id, course_id, feature_date, engagement_ma7, engagement_ma30, engagement_trend FROM temporal_features WHERE feature_date >= NOW() - INTERVAL ':d days'".replace(":d", str(days)))).mappings().all()
        return [dict(r) for r in rows]

@router.post("/pipeline/trigger")
async def trigger_pipeline():
    res = run_pipeline_once()
    return res

@router.get("/pipeline/status")
async def pipeline_status():
    eng = get_analytics_engine()
    with eng.connect() as conn:
        row = conn.execute(text("SELECT run_id, status, records_processed, records_failed FROM pipeline_logs ORDER BY completed_at DESC LIMIT 1")).mappings().first()
        return dict(row) if row else {"status": "none"}

@router.get("/features/temporal/{student_id}")
async def temporal_features(student_id: int):
    eng = get_analytics_engine()
    with eng.connect() as conn:
        rows = conn.execute(text("SELECT * FROM temporal_features WHERE student_id=:sid ORDER BY feature_date DESC"), {"sid": student_id}).mappings().all()
        return [dict(r) for r in rows]

@router.get("/students")
async def list_students(courseId: int | None = None, limit: int = 200):
    eng = get_analytics_engine()
    sql = """
        SELECT sm.student_id AS id,
               AVG(sm.engagement_score) AS engagement,
               AVG(sm.success_rate) AS success_rate
        FROM student_metrics sm
        {where}
        GROUP BY sm.student_id
        ORDER BY sm.student_id
        LIMIT :lim
    """
    where = "WHERE sm.course_id = :cid" if courseId else ""
    q = text(sql.replace("{where}", where))
    params = {"lim": limit}
    if courseId:
        params["cid"] = courseId
    with eng.connect() as conn:
        rows = conn.execute(q, params).mappings().all()
        # Normalize field names for frontend
        out = []
        for r in rows:
            d = dict(r)
            out.append({
                "id": d["id"],
                "name": None,
                "email": None,
                "courseId": courseId,
                "engagement": float(d["engagement"]) if d["engagement"] is not None else None,
                "successRate": float(d["success_rate"]) if d["success_rate"] is not None else None,
            })
        return out
