import json
import re
import hashlib
import os

class DataProcessor:
    def __init__(self, chunk_size=200):
        self.chunk_size = chunk_size
        self.kb = []
        self.seen_hashes = set()

    # ------------------ Cleaning ------------------

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\u00a0', ' ', text)
        return text.strip()

    # ------------------ Chunk-level Deduplication ------------------

    def is_duplicate_chunk(self, text: str) -> bool:
        text_hash = hashlib.md5(text.lower().encode("utf-8")).hexdigest()
        if text_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(text_hash)
        return False

    # ------------------ Chunking ------------------

    def chunk_text(self, text: str):
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size):
            chunk = " ".join(words[i:i + self.chunk_size])
            if len(chunk.split()) >= 40:
                chunks.append(chunk)

        return chunks

    # ------------------ Embedding Enrichment ------------------

    def build_embedding_text(self, record, chunk):
        return (
            f"Loan Name: {record.get('loan_name')} | "
            f"Section: {record.get('section')} | "
            f"Bank: Bank of Maharashtra | "
            f"Content: {chunk}"
        )

    # ------------------ Main Processor ------------------

    def process(self, input_file: str):
        # Resolve path relative to project root
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(base_dir)
        filepath = os.path.join(project_dir, input_file)
        
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        chunk_id = 0

        for record in raw_data:
            raw_text = self.clean_text(record.get("text", ""))
            if len(raw_text) < 80:
                continue

            chunks = self.chunk_text(raw_text)

            for chunk in chunks:
                if self.is_duplicate_chunk(chunk):
                    continue

                embedding_text = self.build_embedding_text(record, chunk)

                self.kb.append({
                    "id": f"chunk_{chunk_id}",
                    "loan_name": record.get("loan_name", "Unknown Loan"),
                    "section": record.get("section", "General"),
                    "text": chunk,                         # used by LLM
                    "embedding_text": embedding_text,     # used by retriever
                    "source_url": record.get("source_url"),
                    "tokens": len(chunk.split())
                })
                chunk_id += 1

        print(
            f"[DONE] Created {len(self.kb)} high-quality RAG chunks "
            f"from {len(raw_data)} raw records"
        )
        return self.kb

    # ------------------ Save ------------------

    def save(self, output_file: str):
        # Resolve path relative to project root
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(base_dir)
        filepath = os.path.join(project_dir, output_file)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.kb, f, indent=2, ensure_ascii=False)

        print(f"[SAVED] Knowledge base → {filepath}")


# ------------------ MAIN ------------------

if __name__ == "__main__":
    processor = DataProcessor(chunk_size=200)
    processor.process("data/raw_loan_data-2.json")
    processor.save("data/knowledge_base-201.json")
