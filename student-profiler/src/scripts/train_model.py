import os
from ..config.database import ensure_schema, fetch_features, FEATURE_COLUMNS, upsert_student_profiles, upsert_profile_definitions, insert_clustering_history
from ..models.clusterer import ClusterPipeline
from ..models.profiler import confidence_from_distances, build_profile_definitions
from ..models.model_manager import save_model
import numpy as np
import json

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")


def main():
    ensure_schema()
    features = fetch_features()
    if not features:
        print("No features available for training")
        return

    X = np.array([[f[c] for c in FEATURE_COLUMNS] for f in features], dtype=float)
    students = [int(f["student_id"]) for f in features]

    pipeline = ClusterPipeline()
    labels, sil, inertia = pipeline.fit(X)
    distances = pipeline.transform_distances(X)
    confs = confidence_from_distances(distances)

    # means per cluster
    cluster_means = {}
    for cid in sorted(set(labels)):
        mask = labels == cid
        group = X[mask]
        means = {FEATURE_COLUMNS[i]: float(group[:, i].mean()) for i in range(len(FEATURE_COLUMNS))}
        means["count"] = int(mask.sum())
        cluster_means[cid] = means

    defs = build_profile_definitions(cluster_means)
    upsert_profile_definitions(defs)

    assignments = []
    for sid, cid, conf in zip(students, labels.tolist(), confs):
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

    print(f"Training complete: version={MODEL_VERSION}, n={meta['n_clusters']}, silhouette={meta['silhouette_score']:.3f}")


if __name__ == "__main__":
    main()
