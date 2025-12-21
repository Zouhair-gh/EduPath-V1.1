from typing import List, Tuple
import numpy as np


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def apply_mmr(candidate_embs: List[np.ndarray], query_emb: np.ndarray, lambda_: float = 0.5, top_n: int = 5) -> List[int]:
    """Return indices of selected candidates balancing relevance vs diversity.
    candidate_embs: list of embeddings for candidates (aligned to candidate list)
    query_emb: query embedding
    lambda_: trade-off between relevance and diversity
    top_n: number of items to select
    """
    selected_idx: List[int] = []
    remaining_idx: List[int] = list(range(len(candidate_embs)))

    while len(selected_idx) < top_n and remaining_idx:
        if not selected_idx:
            # First: most relevant
            best = max(remaining_idx, key=lambda i: cosine_sim(candidate_embs[i], query_emb))
        else:
            scores: List[Tuple[int, float]] = []
            for i in remaining_idx:
                relevance = cosine_sim(candidate_embs[i], query_emb)
                max_similarity = max([cosine_sim(candidate_embs[i], candidate_embs[j]) for j in selected_idx]) if selected_idx else 0.0
                mmr = lambda_ * relevance - (1 - lambda_) * max_similarity
                scores.append((i, mmr))
            best = max(scores, key=lambda x: x[1])[0]
        selected_idx.append(best)
        remaining_idx.remove(best)

    return selected_idx
