import numpy as np
from ..config.database import fetch_resources, upsert_embedding
from ..models.embedder import encode_text

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def main():
    resources = fetch_resources()
    if not resources:
        print("No resources found")
        return
    count = 0
    for r in resources:
        # Update only if missing embedding
        # This simple script re-embeds everything; a smarter one would check a left join
        tags = r.get("tags") or []
        tag_text = ", ".join(tags) if isinstance(tags, list) else str(tags)
        text = f"{r['title']}. {r.get('description','')}. Tags: {tag_text}"
        emb = encode_text(text)
        upsert_embedding(int(r["id"]), emb.tolist(), EMBEDDING_MODEL)
        count += 1
    print(f"Updated embeddings for {count} resources.")

if __name__ == "__main__":
    main()
