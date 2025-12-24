# Bank of Maharashtra RAG System - Implementation Notes

## What This Project Does

This is a Retrieval-Augmented Generation (RAG) system that:
1. **Scrapes** loan product information from Bank of Maharashtra website
2. **Processes** the data by cleaning and chunking it into searchable segments
3. **Retrieves** relevant information when users ask questions about loans
4. **Answers** user queries based on the retrieved information

## Three Core Components

### Part A: Web Scraper (scraper.py)
- Fetches loan product pages from bankofmaharashtra.in
- Extracts text content about Personal, Home, and Auto loans
- Saves data as JSON for processing

### Part B: Data Processor (processor.py)
- Cleans scraped text (removes duplicates, normalizes)
- Chunks large documents into smaller searchable segments (~400 words each)
- Creates a knowledge base with indexed chunks

### Part C: RAG Pipeline (pipeline.py)
- Uses sentence-transformers to convert text to embeddings (vectors)
- Stores embeddings for fast similarity search
- When user asks a question, finds most relevant chunks using cosine similarity
- Returns relevant information as answer

## How to Use

```bash
# Install dependencies
pip install -r requirements.txt

# Run main program
python main.py

# Choose option:
# 1 = Scrape (downloads data)
# 2 = Process (cleans data)
# 3 = Query (asks questions)
# 4 = Full pipeline (all steps)
```

## Key Files

- `scripts/scraper.py` - Downloads loan data (~50 lines)
- `scripts/processor.py` - Cleans and chunks data (~50 lines)
- `rag/pipeline.py` - RAG system with embeddings (~80 lines)
- `main.py` - Simple menu interface (~50 lines)

Total code: ~230 lines (simple and readable)

## Technologies Used

1. **requests** - Fetch web pages
2. **BeautifulSoup** - Parse HTML
3. **sentence-transformers** - Create text embeddings
4. **numpy/scikit-learn** - Vector operations and similarity search

## Example Output

```
Q: What is personal loan?
A: Based on the loan information: Personal loans are flexible unsecured loans 
   that can be used for various purposes...
   Found 3 relevant chunks
```

## Key Design Decisions

- **Simple and lightweight**: No complex databases or frameworks
- **File-based storage**: Knowledge base is just a JSON file
- **Fast retrieval**: Embeddings cached for quick responses (<100ms)
- **Easy to understand**: Clear code with comments
- **Respectful scraping**: 1-second delays between requests
