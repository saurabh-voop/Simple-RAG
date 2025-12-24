# Bank of Maharashtra Loan RAG System

A simple Retrieval-Augmented Generation (RAG) system that scrapes Bank of Maharashtra loan information and answers user questions about loans.

## Project Structure

```
simple-RAG/
├── data/                  # Data files
├── scripts/
│   ├── scraper.py         # Web scraper
│   └── processor.py       # Data processor
├── rag/
│   └── pipeline.py        # RAG system
├── main.py               # Main script
└── requirements.txt      # Dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Choose from menu:
1. **Scrape** - Download loan data from Bank of Maharashtra
2. **Process** - Clean and create knowledge base
3. **Query** - Ask questions about loans (interactive)
4. **Full Pipeline** - Run all steps

## How It Works

### Part A: Web Scraping
Scrapes Bank of Maharashtra website for loan product information from sections like:
- Personal Loans
- Home Loans
- Auto Loans

### Part B: Data Processing
- Cleans scraped text
- Removes duplicates
- Chunks text into searchable segments
- Creates knowledge base (JSON format)

### Part C: RAG Pipeline
1. User asks a question
2. Question is converted to embedding (vector)
3. System searches knowledge base for similar chunks
4. Returns relevant information as answer

## Example Queries

```
"What is a personal loan?"
"Tell me about home loan eligibility"
"How to apply for auto loan?"
"What documents are needed for loans?"
```

## Technologies Used

- **requests** - Web scraping
- **BeautifulSoup4** - HTML parsing
- **sentence-transformers** - Semantic embeddings
- **numpy** - Vector operations
- **scikit-learn** - Similarity search

## Requirements

- Python 3.8+
- Internet connection (for scraping)
- ~500MB disk space (for embeddings model)

## Output Files

- `data/raw_data.json` - Scraped loan data
- `data/knowledge_base.json` - Processed knowledge base

