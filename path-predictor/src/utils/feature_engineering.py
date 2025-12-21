from typing import List, Dict, Any
import numpy as np

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


def to_matrix(rows: List[Dict[str, Any]]) -> np.ndarray:
    X = np.array([[float(r.get(c, 0.0)) for c in FEATURE_COLUMNS] for r in rows], dtype=float)
    return X


def single_to_vector(row: Dict[str, Any]) -> np.ndarray:
    return np.array([float(row.get(c, 0.0)) for c in FEATURE_COLUMNS], dtype=float)
