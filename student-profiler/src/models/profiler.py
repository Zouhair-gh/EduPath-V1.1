from typing import List, Dict, Any, Tuple
import numpy as np

PROFILE_LABELS = {
    0: "Assidu Excellence",
    1: "Assidu Moyen",
    2: "Procrastinateur",
    3: "En Difficulté",
    4: "Décrocheur",
}


def interpret_cluster(avg_engagement: float, avg_success: float, avg_punctuality: float) -> Tuple[int, str, str]:
    # Rule-based interpretation aligned with specification thresholds
    if avg_engagement > 80 and avg_success > 85 and avg_punctuality > 90:
        return 0, PROFILE_LABELS[0], "Très engagé, excellent réussite, ponctualité élevée"
    if avg_engagement > 60 and 60 <= avg_success <= 80 and avg_punctuality > 70:
        return 1, PROFILE_LABELS[1], "Engagé, réussite correcte, ponctuel"
    if avg_punctuality < 50 and 40 <= avg_engagement <= 70 and 40 <= avg_success <= 70:
        return 2, PROFILE_LABELS[2], "Tendance à remettre au lendemain, ponctualité faible"
    if avg_engagement < 50 and avg_success < 50:
        return 3, PROFILE_LABELS[3], "Besoin d'accompagnement, difficultés multiples"
    if avg_engagement < 30 and avg_success < 40:
        return 4, PROFILE_LABELS[4], "Très faible engagement, risque de décrochage"
    # Fallback: choose closest among defined types by heuristic
    return 1, PROFILE_LABELS[1], "Profil intermédiaire"


def confidence_from_distances(distances: np.ndarray) -> List[float]:
    # distances: shape (n_samples, n_clusters), use min distance
    mins = distances.min(axis=1)
    # Normalize to 0-100: assume typical distances in [0, 10]
    scores = (10.0 - mins) / 10.0 * 100.0
    return [float(max(0.0, min(100.0, s))) for s in scores]


def build_profile_definitions(cluster_means: Dict[int, Dict[str, float]]) -> List[Dict[str, Any]]:
    defs: List[Dict[str, Any]] = []
    for cid, means in sorted(cluster_means.items()):
        pid, label, description = interpret_cluster(
            means.get("engagement_score", 0.0),
            means.get("success_rate", 0.0),
            means.get("punctuality_score", 0.0),
        )
        defs.append({
            "profile_id": pid,
            "label": label,
            "description": description,
            "avg_engagement": round(means.get("engagement_score", 0.0), 2),
            "avg_success_rate": round(means.get("success_rate", 0.0), 2),
            "avg_punctuality": round(means.get("punctuality_score", 0.0), 2),
            "student_count": int(means.get("count", 0)),
        })
    return defs
