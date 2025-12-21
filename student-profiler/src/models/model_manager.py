import os
from typing import Any, Dict
import json
import joblib
from datetime import datetime

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0")


def ensure_models_dir() -> None:
    os.makedirs(MODELS_DIR, exist_ok=True)


def model_path(version: str | None = None) -> str:
    ensure_models_dir()
    v = version or MODEL_VERSION
    return os.path.join(MODELS_DIR, f"model_{v}.pkl")


def metadata_path(version: str | None = None) -> str:
    ensure_models_dir()
    v = version or MODEL_VERSION
    return os.path.join(MODELS_DIR, f"model_{v}.meta.json")


def save_model(pipeline: Any, meta: Dict[str, Any]) -> str:
    ensure_models_dir()
    pkl_path = model_path()
    joblib.dump(pipeline, pkl_path)
    meta["saved_at"] = datetime.utcnow().isoformat()
    with open(metadata_path(), "w", encoding="utf-8") as f:
        json.dump(meta, f)
    return pkl_path


def load_model(version: str | None = None) -> Any | None:
    pkl_path = model_path(version)
    if not os.path.exists(pkl_path):
        return None
    return joblib.load(pkl_path)


def load_metadata(version: str | None = None) -> Dict[str, Any]:
    m_path = metadata_path(version)
    if not os.path.exists(m_path):
        return {}
    with open(m_path, "r", encoding="utf-8") as f:
        return json.load(f)
