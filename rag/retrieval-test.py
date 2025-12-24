import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ------------------ Paths ------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(base_dir)
kb_path = os.path.join(project_dir, "data", "knowledge_base-1.json")

# ------------------ Load KB ------------------
with open(kb_path, "r", encoding="utf-8") as f:
    kb = json.load(f)

texts = [item["text"] for item in kb]

# ------------------ Embedding Model ------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

print("[INFO] Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# ------------------ Build FAISS Index ------------------
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
print(f"[INFO] Indexed {index.ntotal} chunks")

# ------------------ Retrieval Function ------------------
def search(query, top_k=5, threshold=0.55):
    """
    Search the FAISS index for top_k relevant chunks for a given query.
    threshold: cosine similarity threshold for filtering weak results.
    """
    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        # Convert L2 distance to approximate cosine similarity (optional)
        score = 1 / (1 + dist)
        if score < threshold:
            continue

        item = kb[idx]
        results.append({
            "loan_name": item.get("loan_name", "Unknown Loan"),
            "section": item.get("section", "General"),
            "text": item["text"][:300] + ("..." if len(item["text"]) > 300 else ""),
            "source_url": item.get("source_url", ""),
            "score": round(score, 3)
        })
    return results

# ------------------ Test Queries ------------------
queries = [
    "What is the interest rate for home loan?",
    "Documents required for gold loan",
    "Eligibility for education loan",
    "Processing fees for car loan"
]

for q in queries:
    print(f"\nQUERY: {q}")
    print("-" * 80)
    results = search(q, top_k=5)
    if not results:
        print("[INFO] No relevant chunks found for this query")
        continue
    for r in results:
        print(f"[{r['loan_name']} | {r['section']}] (Score: {r['score']})")
        print(r["text"])
        print(f"Source: {r['source_url']}")
        print()
