from src.models.embedder import encode_text

def test_encode_text_shape():
    emb = encode_text("algebra basics")
    assert len(emb.shape) == 1
    assert emb.shape[0] == 384