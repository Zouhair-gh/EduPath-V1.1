import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..config.database import ensure_schema, fetch_features, FEATURE_COLUMNS, get_engine, upsert_student_profiles, upsert_profile_definitions, insert_clustering_history, latest_metrics
from ..models.clusterer import ClusterPipeline
from ..models.profiler import confidence_from_distances, build_profile_definitions
from .schemas import StudentProfile, ProfileDefinition, DistributionItem, Metrics, Visualization, RetrainResponse
from ..models.model_manager import save_model, load_model, load_metadata
from ..utils.visualization import pca_scatter_base64
import numpy as np
import json

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")

# Global in-memory model
_model: ClusterPipeline | None = None


def _load_or_init_model() -> ClusterPipeline | None:
    global _model
    if _model is not None:
        return _model
    m = load_model()
    if m is not None:
        _model = m
    return _model


# Model will be lazy-loaded on first use; schema ensured in app startup.


@router.get("/student/{student_id}", response_model=StudentProfile)
async def get_student_profile(student_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text(
            "SELECT * FROM student_profiles WHERE student_id = :sid ORDER BY assigned_at DESC LIMIT 1"
        ), {"sid": student_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found for student")
    return StudentProfile(**dict(row))


@router.get("/definitions", response_model=List[ProfileDefinition])
async def get_definitions():
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM profile_definitions ORDER BY profile_id ASC")).mappings().all()
    return [ProfileDefinition(**dict(r)) for r in rows]


@router.get("/distribution", response_model=List[DistributionItem])
async def get_distribution():
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text(
            "SELECT profile_label, COUNT(*) as count FROM student_profiles GROUP BY profile_label"
        )).mappings().all()
    total = sum(r["count"] for r in rows) or 1
    return [DistributionItem(profile_label=r["profile_label"], count=r["count"], percentage=round(100.0 * r["count"]/total, 2)) for r in rows]


@router.post("/retrain", response_model=RetrainResponse)
async def retrain_model():
    features = fetch_features()
    if not features:
        raise HTTPException(status_code=400, detail="No features available for training")

    X = np.array([[f[c] for c in FEATURE_COLUMNS] for f in features], dtype=float)
    students = [int(f["student_id"]) for f in features]

    pipeline = ClusterPipeline()
    labels, sil, inertia = pipeline.fit(X)
    distances = pipeline.transform_distances(X)
    confs = confidence_from_distances(distances)

    # Compute means per cluster
    cluster_means: Dict[int, Dict[str, float]] = {}
    for cid in sorted(set(labels)):
        mask = labels == cid
        group = X[mask]
        means = {FEATURE_COLUMNS[i]: float(group[:, i].mean()) for i in range(len(FEATURE_COLUMNS))}
        means["count"] = int(mask.sum())
        cluster_means[cid] = means

    # Build profile definitions and persist
    defs = build_profile_definitions(cluster_means)
    upsert_profile_definitions(defs)

    # Assign students
    assignments: List[Dict[str, Any]] = []
    for sid, cid, conf in zip(students, labels.tolist(), confs):
        # find label from definitions by profile_id mapping; fall back
        prof = next((d for d in defs if d["profile_id"] == cid), None)
        label = prof["label"] if prof else f"Cluster {cid}"
        assignments.append({
            "student_id": sid,
            "profile_id": cid,
            "profile_label": label,
            "confidence_score": round(conf, 2),
            "model_version": MODEL_VERSION,
        })
    upsert_student_profiles(assignments)

    # Save model and history
    meta = pipeline.to_metadata() | {
        "model_version": MODEL_VERSION,
        "silhouette_score": float(sil),
        "inertia": float(inertia),
        "features_used": FEATURE_COLUMNS,
    }
    save_model(pipeline, meta)
    insert_clustering_history({
        "model_version": MODEL_VERSION,
        "n_clusters": meta["n_clusters"],
        "silhouette_score": meta["silhouette_score"],
        "inertia": meta["inertia"],
        "features_used": json.dumps(FEATURE_COLUMNS),
    })

    # Store model in memory
    global _model
    _model = pipeline

    return RetrainResponse(
        model_version=MODEL_VERSION,
        n_clusters=meta["n_clusters"],
        silhouette_score=meta["silhouette_score"],
        inertia=meta["inertia"],
        assigned_count=len(assignments),
    )


@router.get("/metrics", response_model=Metrics)
async def get_metrics():
    m = latest_metrics()
    if not m:
        raise HTTPException(status_code=404, detail="No metrics available")
    return Metrics(
        model_version=m["model_version"],
        n_clusters=int(m["n_clusters"]),
        silhouette_score=float(m["silhouette_score"]),
        inertia=float(m["inertia"]),
    )


@router.get("/visualization", response_model=Visualization)
async def get_visualization():
    pipeline = _load_or_init_model()
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Model not loaded. Retrain first.")
    features = fetch_features()
    if not features:
        raise HTTPException(status_code=400, detail="No features available for visualization")
    X = np.array([[f[c] for c in FEATURE_COLUMNS] for f in features], dtype=float)
    labels = pipeline.predict(X)
    embedding = pipeline.project(X)
    img_b64 = pca_scatter_base64(embedding, labels.tolist())
    return Visualization(image_base64=img_b64)
