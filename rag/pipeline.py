# ------------------------------ RAG Pipeline: Bank of Maharashtra Loans ------------------------------

import os
import json
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

KB_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss.index")
EMB_FILE = os.path.join(DATA_DIR, "embeddings.npy")

# ------------------ Data Processor ------------------

class DataProcessor:
    def __init__(self, chunk_size=350):
        self.chunk_size = chunk_size
        self.overlap = 50  # 50-word overlap for context
        self.kb = []

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\u00a0', ' ', text)
        return text.strip()

    def chunk_text(self, text):
        words = text.split()
        chunks = []
        
        # Overlapping chunks
        step = self.chunk_size - self.overlap  # 300-word step with 50-word overlap
        for i in range(0, len(words), step):
            chunk = " ".join(words[i:i + self.chunk_size])
            if len(chunk.split()) >= 80:  # Minimum 80 words
                chunks.append(chunk)
            
            # Stop if near end
            if i + self.chunk_size >= len(words):
                break
        
        return chunks

    def process(self, input_file):
        # Resolve file path from project root
        raw_file = os.path.join(PROJECT_DIR, input_file)
        
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        chunk_id = 0
        for record in raw_data:
            text = self.clean_text(record.get("text", ""))
            if len(text) < 80:
                continue

            chunks = self.chunk_text(text)
            for chunk in chunks:
                # Contextualized embedding text
                embedding_text = (
                    f"Loan: {record.get('loan_name')} | "
                    f"Section: {record.get('section')} | "
                    f"Content: {chunk}"
                )
                
                self.kb.append({
                    "id": f"chunk_{chunk_id}",
                    "loan_name": record.get("loan_name"),
                    "section": record.get("section"),
                    "text": chunk,
                    "embedding_text": embedding_text,
                    "source_url": record.get("source_url")
                })
                chunk_id += 1

        print(f"[INFO] Created {len(self.kb)} chunks from {len(raw_data)} records")
        return self.kb

    def save(self, output_file):
        output_path = os.path.join(DATA_DIR, output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.kb, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Knowledge base saved → {output_path}")

# ------------------ Retriever: Semantic Search ------------------

class Retriever:
    def __init__(self):
        # Load KB
        with open(KB_FILE, "r", encoding="utf-8") as f:
            self.kb = json.load(f)

        self.texts = [chunk["embedding_text"] for chunk in self.kb]
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Build/load FAISS index
        if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(EMB_FILE):
            print("[INFO] Loading cached embeddings and FAISS index")
            self.embeddings = np.load(EMB_FILE)
            self.index = faiss.read_index(FAISS_INDEX_FILE)
        else:
            print("[INFO] Creating embeddings (one-time process)...")
            self.embeddings = self.model.encode(
                self.texts,
                normalize_embeddings=True,
                show_progress_bar=True
            ).astype("float32")
            
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)  # Inner Product for cosine similarity
            self.index.add(self.embeddings)
            
            faiss.write_index(self.index, FAISS_INDEX_FILE)
            np.save(EMB_FILE, self.embeddings)
            print(f"[INFO] Embeddings cached ({self.index.ntotal} vectors)")

        print(f"[INFO] Retriever ready with {len(self.kb)} chunks")

    def search(self, query, top_k=5):
        """Semantic search using FAISS IndexFlatIP"""
        # Encode query with same normalization
        query_emb = self.model.encode(
            [query],
            normalize_embeddings=True
        ).astype("float32")

        # Search FAISS (returns cosine similarity scores 0-1)
        scores, indices = self.index.search(query_emb, min(top_k * 3, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # Invalid index
                continue
            
            item = self.kb[int(idx)]
            
            # Score threshold to filter out irrelevant results
            if score < 0.20:  # Lower threshold = more inclusive
                continue
            
            results.append({
                "loan_name": item["loan_name"],
                "section": item["section"],
                "text": item["text"],
                "source_url": item["source_url"],
                "score": float(score)
            })

        # Return top-k sorted by score
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return results[:top_k]

# ------------------ Answer Generator ------------------

class AnswerGenerator:
    def __init__(self):
        self.generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )

    def generate(self, query, chunks):
        if not chunks:
            return "Information not available in the knowledge base."
        
        # Format context from retrieved chunks
        context = "\n\n".join(
            f"[{c['loan_name']} | {c['section']}]\n{c['text']}"
            for c in chunks
        )

        prompt = f"""Answer the question strictly using the context provided.
If the exact information is not available, provide the closest relevant answer.
Always include numeric values when mentioned.

Context:
{context}

Question: {query}

Answer:"""

        output = self.generator(prompt, max_length=400, do_sample=False)
        answer = output[0]["generated_text"].strip()
        
        return answer

# ------------------ MAIN ------------------

if __name__ == "__main__":
    # ---- Create KB if doesn't exist ----
    if not os.path.exists(KB_FILE):
        print("[INFO] Building knowledge base...")
        processor = DataProcessor()
        processor.process("data/raw_loan_data-2.json")
        processor.save("knowledge_base.json")

    retriever = Retriever()
    generator = AnswerGenerator()

    print("\n" + "="*80)
    print("BANK OF MAHARASHTRA LOAN RAG SYSTEM")
    print("="*80)
    print("Ask questions about loans (type 'exit' to quit)\n")

    while True:
        query = input("Query: ").strip()
        if query.lower() == "exit":
            break
        
        if not query:
            print("Please enter a query.\n")
            continue

        # Retrieve relevant chunks
        chunks = retriever.search(query, top_k=5)
        
        if not chunks:
            print("\n❌ No relevant information found.\n")
            continue

        # Show retrieved chunks
        print("\n📚 Retrieved Information:")
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] {chunk['loan_name']} - {chunk['section']} (Score: {chunk['score']:.3f})")
            print(f"      {chunk['text'][:80]}...")

        # Generate answer
        print("\n💡 Answer:")
        answer = generator.generate(query, chunks)
        print(answer)
        print("\n" + "-"*80 + "\n")
