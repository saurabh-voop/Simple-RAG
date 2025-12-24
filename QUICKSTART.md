# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the System
```bash
python main.py
```

Choose one of three options:
- **Option 1**: Full pipeline (Scrape → Process → Query)
- **Option 2**: Query only (if knowledge base exists)
- **Option 3**: Interactive Q&A mode

---

## Complete Step-by-Step

### Step 1: Scrape Bank of Maharashtra Website
```bash
cd scripts
python scraper.py
```
**Output**: 
- `data/raw_loan_data.json`
- `data/raw_loan_data.txt`

### Step 2: Process & Create Knowledge Base
```bash
python processor.py
```
**Output**:
- `data/knowledge_base.json` (Searchable KB)
- `data/knowledge_base.txt` (Human-readable)

### Step 3: Query with RAG Pipeline
```bash
cd ../rag
python pipeline.py
```

**Or use interactively in Python:**
```python
from pipeline import RAGPipeline

rag = RAGPipeline('../data/knowledge_base.json')
result = rag.query("What are personal loan eligibility criteria?")
print(result['answer'])
```

---

## What Each Script Does

### `scripts/scraper.py` (Part A)
```
Bank of Maharashtra Website
    ↓
Scrapes Loan Sections
    ↓
Extracts Text Content
    ↓
Saves as JSON & Text
```

### `scripts/processor.py` (Part B)
```
Raw Loan Data
    ↓
Clean Text
    ↓
Remove Duplicates
    ↓
Create Chunks
    ↓
Structured Knowledge Base
```

### `rag/pipeline.py` (Part C)
```
User Question
    ↓
Convert to Embedding
    ↓
Search Knowledge Base
    ↓
Retrieve Relevant Chunks
    ↓
Generate Answer
```

---

## Example Queries

Ask any of these questions:
- "What are personal loan eligibility criteria?"
- "Tell me about home loan features and benefits"
- "What documents do I need for auto loan?"
- "How to apply for business loan?"
- "What is the interest rate for education loans?"
- "Tell me about loan against property"

---

## Understanding the Output

### RAG Query Result
```python
{
    'question': 'Your question here',
    
    'relevant_chunks': [
        {
            'text': 'Relevant information...',
            'loan_type': 'Personal Loan',
            'title': 'Eligibility Criteria',
            'similarity_score': 0.92  # How relevant (0-1)
        },
        ...  # More chunks
    ],
    
    'answer': 'Generated response based on retrieved info'
}
```

### Key Metrics
- **similarity_score**: 0-1 scale, higher = more relevant
- **word_count**: Size of each chunk
- **loan_type**: Category of loan information

---

## Common Issues & Solutions

### "Module not found" Error
```bash
# Add scripts directory to Python path
export PYTHONPATH="${PYTHONPATH}:./scripts"
```

### Slow First Run
- First run generates embeddings (~2-5 minutes)
- Subsequent runs use cache (<1 second startup)

### No Results for Query
- Try rephrasing question
- Increase number of retrieved chunks (top_k=5)
- Lower similarity threshold (threshold=0.2)

### Memory Issues
- Use smaller embedding model: `paraphrase-MiniLM-L6-v2`
- Process data in batches

---

## Project Structure Overview

```
simple-RAG/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── README.md                  # Full documentation
├── QUICKSTART.md              # This file
│
├── scripts/
│   ├── scraper.py             # Web scraper (Part A)
│   └── processor.py           # Data processor (Part B)
│
├── rag/
│   ├── __init__.py
│   └── pipeline.py            # RAG pipeline (Part C)
│
└── data/
    ├── raw_loan_data.json
    ├── knowledge_base.json    # Main KB file
    └── knowledge_base_embeddings.json
```

---

## For Interview/Assessment

### Demonstrate Understanding:
1. **Part A**: Run scraper, show collected data
2. **Part B**: Show processed knowledge base quality
3. **Part C**: Run sample queries, show retrieval accuracy

### Talking Points:
- "Web scraping respects robots.txt and uses delays"
- "Chunking strategy balances context and efficiency"
- "Semantic embeddings find meaning-based matches"
- "Similarity scoring ranks relevance automatically"
- "Caching embeddings improves startup performance"

### Potential Questions:
- **How does similarity work?**: Cosine distance in embedding space
- **Why chunking?**: Optimal balance between context and precision
- **Scale to large data?**: Can handle 100K+ chunks efficiently
- **Add LLM?**: Simple integration with OpenAI/HuggingFace APIs
- **Improve retrieval?**: Adjust threshold, use reranking, query expansion

---

## Next Steps

1. **Customize Scraper**: Add more specific sections
2. **Improve Embeddings**: Try `all-mpnet-base-v2` for better quality
3. **Add LLM**: Integrate with OpenAI/Hugging Face
4. **Create Web UI**: Flask/Streamlit interface
5. **Add Tests**: Unit tests for each component
6. **Deploy**: Docker container for production

---

**Ready to start? Run `python main.py` now! 🚀**
