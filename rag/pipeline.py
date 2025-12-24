# ------------------------------ full_rag_pipeline_final.py ------------------------------

import json
import re
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

KB_FILE = os.path.join(DATA_DIR, "knowledge_base-200.json")
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss.index")
EMB_FILE = os.path.join(DATA_DIR, "embeddings.npy")


# ------------------ Phase 1: Data Processing (Run Once) ------------------

class DataProcessor:
    def __init__(self):
        self.kb = []

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def chunk_text(self, text, size=200):
        words = text.split()
        chunks = []
        for i in range(0, len(words), size):
            chunk = " ".join(words[i:i + size])
            if len(chunk) > 80:
                chunks.append(chunk)
        return chunks

    def process(self, input_file):
        input_file = os.path.join(PROJECT_DIR, input_file)

        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunk_id = 0
        for item in data:
            text = self.clean_text(item.get("text", ""))
            if len(text) < 80:
                continue

            for chunk in self.chunk_text(text):
                self.kb.append({
                    "id": f"chunk_{chunk_id}",
                    "loan_name": item.get("loan_name", "Unknown Loan"),
                    "section": item.get("section", "General"),
                    "text": chunk,
                    "source_url": item.get("source_url", "")
                })
                chunk_id += 1

        print(f"[INFO] Created {len(self.kb)} chunks from {len(data)} records")

    def save(self):
        with open(KB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.kb, f, indent=2, ensure_ascii=False)

        print(f"[INFO] Knowledge base saved → {KB_FILE}")


# ------------------ Phase 2: Retrieval ------------------

class Retriever:
    def __init__(self):
        with open(KB_FILE, "r", encoding="utf-8") as f:
            self.kb = json.load(f)

        self.texts = [item["text"] for item in self.kb]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(EMB_FILE):
            print("[INFO] Loading cached embeddings and FAISS index")
            self.embeddings = np.load(EMB_FILE)
            self.index = faiss.read_index(FAISS_INDEX_FILE)
        else:
            print("[INFO] Creating embeddings (one-time)")
            self.embeddings = self.model.encode(
                self.texts,
                normalize_embeddings=True,
                show_progress_bar=True
            ).astype("float32")

            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(self.embeddings)

            faiss.write_index(self.index, FAISS_INDEX_FILE)
            np.save(EMB_FILE, self.embeddings)

        print(f"[INFO] Indexed {self.index.ntotal} chunks")

    def search(self, query, top_k=6, min_score=0.25):
        query_emb = self.model.encode(
            [query],
            normalize_embeddings=True
        ).astype("float32")

        scores, indices = self.index.search(query_emb, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score < min_score:
                continue

            item = self.kb[idx]
            results.append({
                "loan_name": item["loan_name"],
                "section": item["section"],
                "text": item["text"],
                "source_url": item["source_url"],
                "score": float(score)
            })

        return results


# ------------------ Phase 3: Answer Generation (With Memory) ------------------

class AnswerGenerator:
    def __init__(self):
        self.generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )
        self.chat_history = []

    def generate(self, query, chunks):
        context = "\n\n".join(
            f"[{c['loan_name']} | {c['section']}]\n{c['text']}"
            for c in chunks
        )

        history = "\n".join(self.chat_history[-4:])

        prompt = f"""
You are a banking assistant.

Conversation so far:
{history}

Context:
{context}

Question:
{query}

Answer strictly using the context.
If information is missing, say "Information not available".
"""

        output = self.generator(prompt, max_length=350, do_sample=False)
        answer = output[0]["generated_text"]

        self.chat_history.append(f"User: {query}")
        self.chat_history.append(f"Assistant: {answer}")

        return answer


# ------------------ MAIN (Interactive) ------------------

if __name__ == "__main__":

    # ---- Run Phase 1 only if KB does not exist ----
    if not os.path.exists(KB_FILE):
        processor = DataProcessor()
        processor.process("data/raw_loan_data-1.json")
        processor.save()

    retriever = Retriever()
    generator = AnswerGenerator()

    print("\nAsk questions about bank loans (type 'exit' to quit)\n")

    while True:
        query = input("Query: ").strip()
        if query.lower() == "exit":
            break

        retrieved = retriever.search(query)

        if not retrieved:
            print("No relevant information found.\n")
            continue

        answer = generator.generate(query, retrieved)

        print("\nAnswer:")
        print(answer)
        print("-" * 80)
