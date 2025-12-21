import numpy as np
from src.utils.diversity import apply_mmr

def test_mmr_selects_top_n():
    # Create simple candidate embeddings
    candidates = [np.array([1,0,0], dtype=np.float32), np.array([0.9,0.1,0], dtype=np.float32), np.array([0,1,0], dtype=np.float32)]
    query = np.array([1,0,0], dtype=np.float32)
    selected = apply_mmr(candidates, query, lambda_=0.5, top_n=2)
    assert len(selected) == 2
    assert 0 in selected
