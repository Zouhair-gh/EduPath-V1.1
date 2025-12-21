import numpy as np
from ..config.database import fetch_features, FEATURE_COLUMNS
from ..models.predictor import Predictor


def main():
    rows = fetch_features()
    rows = [r for r in rows if r.get('passed') is not None]
    if not rows:
        print("No labeled data for evaluation")
        return
    X = np.array([[float(r.get(c, 0.0)) for c in FEATURE_COLUMNS] for r in rows], dtype=float)
    y = np.array([int(r['passed']) for r in rows], dtype=int)
    model = Predictor()
    metrics = model.fit_cv(X, y)
    print(f"CV Metrics: AUC={metrics['auc_mean']:.3f} F1={metrics['f1_mean']:.3f} P={metrics['precision_mean']:.3f} R={metrics['recall_mean']:.3f}")


if __name__ == "__main__":
    main()
