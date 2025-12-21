import numpy as np
from ..config.database import fetch_resources, upsert_embedding
from ..models.embedder import encode_text
from ..models.faiss_index import build_index, save_index

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def main():
    resources = fetch_resources()
    if not resources:
        print("No resources to index")
        return
    texts = []
    ids = []
    for r in resources:
        tags = r.get("tags") or []
        tag_text = ", ".join(tags) if isinstance(tags, list) else str(tags)
        text = f"{r['title']}. {r.get('description','')}. Tags: {tag_text}"
        texts.append(text)
        ids.append(int(r["id"]))
    embeddings = np.vstack([encode_text(t) for t in texts])

    for rid, emb in zip(ids, embeddings):
        upsert_embedding(rid, emb.tolist(), EMBEDDING_MODEL)

    build_index(embeddings, np.array(ids, dtype=np.int64))
    save_index()
    print(f"Indexed {len(ids)} resources and saved FAISS index.")

if __name__ == "__main__":
    main()
