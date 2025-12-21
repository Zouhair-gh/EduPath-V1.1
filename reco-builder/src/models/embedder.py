from typing import List
import os
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LOCAL_MODEL_DIR = os.getenv("LOCAL_MODEL_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/sentence_transformer")))

_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        try:
            # Try local model directory if present
            if os.path.isdir(LOCAL_MODEL_DIR) and any(os.scandir(LOCAL_MODEL_DIR)):
                _model = SentenceTransformer(LOCAL_MODEL_DIR)
            else:
                _model = SentenceTransformer(MODEL_NAME)
        except Exception:
            # Fallback to remote model name
            _model = SentenceTransformer(MODEL_NAME)
    return _model


def encode_text(text: str) -> np.ndarray:
    model = get_model()
    emb = model.encode(text, normalize_embeddings=True)
    return np.asarray(emb, dtype=np.float32)


def encode_batch(texts: List[str]) -> np.ndarray:
    model = get_model()
    embs = model.encode(texts, normalize_embeddings=True)
    return np.asarray(embs, dtype=np.float32)
