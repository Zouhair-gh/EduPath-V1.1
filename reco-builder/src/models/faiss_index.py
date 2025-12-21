import os
from typing import Tuple
import numpy as np
import faiss

INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../indexes/faiss.index"))
DIM = 384

_index: faiss.Index | None = None
_resource_ids: np.ndarray | None = None


def build_index(embeddings: np.ndarray, resource_ids: np.ndarray) -> None:
    global _index, _resource_ids
    idx = faiss.IndexFlatIP(DIM)  # use inner product with normalized vectors (cosine)
    idx.add(embeddings)
    _index = idx
    _resource_ids = resource_ids.astype(np.int64)


def save_index() -> None:
    global _index
    if _index is not None:
        faiss.write_index(_index, INDEX_PATH)


def load_index() -> bool:
    global _index
    if os.path.exists(INDEX_PATH):
        _index = faiss.read_index(INDEX_PATH)
        return True
    return False


def search(query_emb: np.ndarray, k: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    global _index
    if _index is None:
        raise RuntimeError("FAISS index not built")
    D, I = _index.search(query_emb.reshape(1, -1), k)
    return D[0], I[0]


def map_indices_to_resource_ids(indices: np.ndarray) -> np.ndarray:
    global _resource_ids
    if _resource_ids is None:
        raise RuntimeError("Resource ID mapping not available")
    return _resource_ids[indices]
