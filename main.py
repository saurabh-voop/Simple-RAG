import sys
import os
from pathlib import Path

sys.path.insert(0, 'scripts')
sys.path.insert(0, 'rag')

from scraper import BankScraper
from processor import DataProcessor
from pipeline import RAGPipeline

def main():
    print("\n=== Bank of Maharashtra Loan RAG ===\n")
    print("1. Scrape data")
    print("2. Process data")
    print("3. Query RAG system")
    print("4. Full pipeline")
    
    choice = input("\nSelect (1-4): ").strip()
    
    if choice == '1':
        print("\nScraping Bank of Maharashtra website...")
        scraper = BankScraper()
        scraper.scrape_loans()
        scraper.save('data/raw_data.json')
        print("✓ Data scraped")
    
    elif choice == '2':
        print("\nProcessing raw data...")
        processor = DataProcessor()
        processor.process('data/raw_data.json')
        processor.save('data/knowledge_base.json')
        print("✓ Data processed")
    
    elif choice == '3':
        print("\nInitializing RAG...")
        rag = RAGPipeline('data/knowledge_base.json')
        
        while True:
            q = input("\nYour question (or 'exit'): ").strip()
            if q.lower() == 'exit':
                break
            
            result = rag.query(q)
            print(f"\nAnswer: {result['answer'][:300]}...")
            print(f"Found {len(result['results'])} relevant chunks\n")
    
    elif choice == '4':
        print("\nRunning full pipeline...\n")
        
        print("Step 1: Scraping...")
        scraper = BankScraper()
        scraper.scrape_loans()
        scraper.save('data/raw_data.json')
        print("✓ Done\n")
        
        print("Step 2: Processing...")
        processor = DataProcessor()
        processor.process('data/raw_data.json')
        processor.save('data/knowledge_base.json')
        print("✓ Done\n")
        
        print("Step 3: Testing RAG...")
        rag = RAGPipeline('data/knowledge_base.json')
        
        test_q = "What is personal loan?"
        result = rag.query(test_q)
        print(f"Q: {test_q}")
        print(f"A: {result['answer'][:200]}...\n")
        print("✓ Done")

if __name__ == "__main__":
    main()
