import os
from ..models.model_manager import load_model, load_metadata
from ..config.database import fetch_features, FEATURE_COLUMNS
import numpy as np

MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")


def main():
    m = load_model(MODEL_VERSION)
    if m is None:
        print("Model not found. Train first.")
        return
    meta = load_metadata(MODEL_VERSION)
    features = fetch_features()
    if not features:
        print("No features available for evaluation")
        return
    X = np.array([[f[c] for c in FEATURE_COLUMNS] for f in features], dtype=float)
    labels = m.predict(X)
    print(f"Model {MODEL_VERSION} loaded. n_clusters={meta.get('n_clusters')} samples={len(labels)}")


if __name__ == "__main__":
    main()
