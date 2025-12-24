"""
Configuration file for RAG System
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'
RAG_DIR = PROJECT_ROOT / 'rag'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)
RAG_DIR.mkdir(exist_ok=True)

# Data file paths
RAW_DATA_JSON = DATA_DIR / 'raw_loan_data.json'
RAW_DATA_TEXT = DATA_DIR / 'raw_loan_data.txt'
KNOWLEDGE_BASE_JSON = DATA_DIR / 'knowledge_base.json'
KNOWLEDGE_BASE_TEXT = DATA_DIR / 'knowledge_base.txt'
EMBEDDINGS_CACHE = DATA_DIR / 'knowledge_base_embeddings.json'

# Scraper configuration
SCRAPER_CONFIG = {
    'base_url': 'https://www.bankofmaharashtra.in',
    'request_delay': 1,  # Seconds between requests
    'timeout': 10,  # Request timeout in seconds
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'loan_sections': [
        'personal-loans',
        'home-loans',
        'auto-loans',
        'education-loans',
        'business-loans',
        'loan-against-property'
    ]
}

# Processor configuration
PROCESSOR_CONFIG = {
    'chunk_size': 500,  # Words per chunk
    'chunk_overlap': 100,  # Overlap between chunks
    'min_content_length': 50,  # Minimum characters for valid content
    'remove_duplicates': True
}

# RAG Pipeline configuration
RAG_CONFIG = {
    'embedding_model': 'all-MiniLM-L6-v2',  # Lightweight, fast model
    'similarity_threshold': 0.3,  # Minimum similarity score
    'top_k': 3,  # Number of chunks to retrieve
    'use_cache': True,  # Use cached embeddings
    'batch_size': 32  # For embedding generation
}

# Alternative embedding models (for reference)
EMBEDDING_MODELS = {
    'lightweight': 'all-MiniLM-L6-v2',  # Recommended (80MB)
    'lightweight_larger': 'all-MiniLM-L12-v2',
    'balanced': 'all-mpnet-base-v2',
    'powerful': 'all-roberta-large-v1'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': PROJECT_ROOT / 'rag_system.log'
}

# Feature flags
FEATURES = {
    'enable_scraping': True,
    'enable_caching': True,
    'enable_logging': True,
    'debug_mode': False
}

# Export configuration
__all__ = [
    'PROJECT_ROOT',
    'DATA_DIR',
    'SCRAPER_CONFIG',
    'PROCESSOR_CONFIG',
    'RAG_CONFIG',
    'FEATURES'
]
