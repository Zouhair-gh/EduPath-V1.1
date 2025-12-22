import os
from typing import List
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from ..config.database import ensure_schema, fetch_resources, fetch_embeddings, upsert_embedding, log_recommendations, insert_feedback, get_student_profile, get_student_difficulties
from ..models.embedder import encode_text
from ..models.faiss_index import build_index, load_index, save_index, search, map_indices_to_resource_ids
from ..models.recommender import get_recommendations
from ..api.schemas import Recommendation, RecommendationsResponse, FeedbackRequest, SearchResponse, Resource, MetricsResponse
from ..config.database import get_engine

router = APIRouter(prefix="/api", tags=["reco-builder"])

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

@router.on_event("startup")
async def startup_event():
    ensure_schema()
    # Try load FAISS index; if not present, build from DB
    if not load_index():
        try:
            embs = fetch_embeddings()
            if embs:
                import numpy as np
                vectors = np.vstack([np.asarray(e["embedding"], dtype=np.float32) for e in embs])
                ids = np.array([int(e["resource_id"]) for e in embs], dtype=np.int64)
                build_index(vectors, ids)
                save_index()
        except Exception as e:
            print(f"[WARN] Failed to build FAISS index on startup: {e}")


@router.get("/resources/search", response_model=SearchResponse)
async def search_resources(q: str = Query(..., min_length=2)):
    # Semantic search using FAISS
    import numpy as np
    try:
        query_emb = encode_text(q)
        D, I = search(query_emb, k=20)
        ids = map_indices_to_resource_ids(I)
    except Exception:
        # Fallback: direct DB LIKE search
        engine = get_engine()
        with engine.begin() as conn:
            rows = conn.execute(text("SELECT id, title, description, resource_type, subject, difficulty_level, url, tags FROM resources WHERE title ILIKE :q OR description ILIKE :q LIMIT 20"), {"q": f"%{q}%"}).mappings().all()
            return SearchResponse(results=[Resource(**dict(r)) for r in rows])

    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, title, description, resource_type, subject, difficulty_level, url, tags FROM resources WHERE id = ANY(:ids)"), {"ids": list(map(int, ids))}).mappings().all()
    return SearchResponse(results=[Resource(**dict(r)) for r in rows])


@router.post("/resources/index")
async def reindex_resources():
    # Build embeddings for all resources and rebuild FAISS index
    import numpy as np
    resources = fetch_resources()
    if not resources:
        raise HTTPException(status_code=404, detail="No resources to index")
    texts: List[str] = []
    ids: List[int] = []
    for r in resources:
        tags = r.get("tags") or []
        if isinstance(tags, list):
            tag_text = ", ".join(tags)
        else:
            tag_text = str(tags)
        text = f"{r['title']}. {r.get('description','')}. Tags: {tag_text}"
        texts.append(text)
        ids.append(int(r["id"]))
    embeddings = encode_text(" ").reshape(1,-1)
    try:
        embeddings = np.vstack([encode_text(t) for t in texts])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

    db_errors = 0
    for rid, emb in zip(ids, embeddings):
        try:
            upsert_embedding(rid, emb.tolist(), EMBEDDING_MODEL)
        except Exception as e:
            db_errors += 1

    try:
        build_index(embeddings, np.array(ids, dtype=np.int64))
        save_index()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAISS index build failed: {e}")

    return {"indexed": len(ids), "db_upserts_failed": db_errors}


@router.get("/recommendations/student/{student_id}", response_model=RecommendationsResponse)
async def recommendations_student(student_id: int, top_n: int = 5):
    profile = get_student_profile(student_id)
    diffs = get_student_difficulties(student_id)
    recos = get_recommendations(student_id, profile_label=profile.get("label","general learner"), difficulties=diffs, top_n=top_n)
    # Log recommendations
    log_recommendations(student_id, recos, context={"difficulties": diffs, "profile": profile.get("label")})
    return RecommendationsResponse(student_id=student_id, recommendations=[Recommendation(**r) for r in recos])


@router.post("/recommendations/feedback")
async def feedback(req: FeedbackRequest):
    insert_feedback(req.recommendation_id, req.student_id, req.action, req.time_spent_seconds)
    return {"status": "ok"}


@router.get("/resources/{resource_id}", response_model=Resource)
async def resource_details(resource_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT id, title, description, resource_type, subject, difficulty_level, url, tags FROM resources WHERE id = :id"), {"id": resource_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Resource not found")
    return Resource(**dict(row))


@router.get("/recommendations/metrics", response_model=MetricsResponse)
async def metrics():
    engine = get_engine()
    with engine.begin() as conn:
        rec_count = conn.execute(text("SELECT COUNT(*) FROM recommendations")).scalar() or 0
        fb_count = conn.execute(text("SELECT COUNT(*) FROM recommendation_feedback")).scalar() or 0
        clicks = conn.execute(text("SELECT COUNT(*) FROM recommendation_feedback WHERE action = 'clicked'")).scalar() or 0
    ctr = float(clicks) / float(rec_count) if rec_count else 0.0
    return MetricsResponse(total_recommendations=int(rec_count), total_feedback=int(fb_count), click_through_rate=ctr)
