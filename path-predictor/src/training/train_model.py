import os
import numpy as np
from ..config.database import ensure_schema, fetch_features, FEATURE_COLUMNS, register_model
from ..config.mlflow_config import setup_mlflow
from ..models.predictor import Predictor

MODEL_NAME = os.getenv("MODEL_NAME", "path-predictor-xgb")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")


def main():
    ensure_schema()
    setup_mlflow()
    rows = fetch_features()
    rows = [r for r in rows if r.get('passed') is not None]
    if not rows:
        print("No labeled historical data available for training")
        return
    X = np.array([[float(r.get(c, 0.0)) for c in FEATURE_COLUMNS] for r in rows], dtype=float)
    y = np.array([int(r['passed']) for r in rows], dtype=int)
    model = Predictor()
    cv_metrics = model.fit_cv(X, y)
    model.fit(X, y)
    run_id, _ = model.log_to_mlflow(cv_metrics)
    register_model(MODEL_NAME, MODEL_VERSION, run_id, 'STAGING', cv_metrics)
    print(f"Training complete: AUC={cv_metrics['auc_mean']:.3f}, run_id={run_id}")


if __name__ == "__main__":
    main()
