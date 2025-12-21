from typing import List, Dict, Any
import numpy as np

from ..models.embedder import encode_text
from ..models.faiss_index import search, map_indices_to_resource_ids
from ..utils.diversity import apply_mmr
from ..config.database import get_engine, recently_viewed


def get_recommendations(student_id: int, profile_label: str, difficulties: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
    # 1. Build query text
    diff_text = ", ".join(difficulties) if difficulties else "fundamentals"
    query = f"{profile_label}. Difficulties: {diff_text}"
    q_emb = encode_text(query)

    # 2. Search FAISS
    D, I = search(q_emb, k=max(50, top_n * 10))
    resource_ids = map_indices_to_resource_ids(I)

    # 3. Fetch embeddings for selected resources to compute diversity
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            "SELECT r.id, r.title, r.description, r.difficulty_level, r.url, e.embedding FROM resources r JOIN resource_embeddings e ON e.resource_id = r.id WHERE r.id = ANY(:ids)",
            {"ids": list(map(int, resource_ids))}
        ).fetchall()

    candidate_embs: List[np.ndarray] = []
    candidates: List[Dict[str, Any]] = []
    for rid, title, desc, level, url, emb in rows:
        candidate_embs.append(np.asarray(emb, dtype=np.float32))
        candidates.append({
            "resource_id": int(rid),
            "title": title,
            "description": desc,
            "difficulty_level": level,
            "url": url,
        })

    # 4. Diversify via MMR
    selected_indices = apply_mmr(candidate_embs, q_emb, lambda_=0.5, top_n=top_n)

    # 5. Exclude recently viewed
    final: List[Dict[str, Any]] = []
    for idx in selected_indices:
        c = candidates[idx]
        if not recently_viewed(student_id, c["resource_id"], days=7):
            final.append({**c, "score": float(D[idx])})
        if len(final) >= top_n:
            break

    return final
