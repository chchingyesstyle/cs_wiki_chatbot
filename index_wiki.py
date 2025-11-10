#!/usr/bin/env python3
"""
Script to index MediaWiki pages into vector database
Run this once to populate the vector store, or when wiki content changes
"""

from db_connector import WikiDBConnector
from vector_store import VectorStore
from chatbot import WikiChatbot
import sys

def main():
    print("=" * 60)
    print("MediaWiki Vector Database Indexer")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Connecting to database...")
    db = WikiDBConnector()
    if not db.connect():
        print("❌ Failed to connect to database")
        sys.exit(1)
    
    print("✓ Database connected")
    
    # Get all pages from wiki
    print("\n2. Fetching all wiki pages...")
    pages = db.get_all_pages(limit=10000)  # Adjust limit as needed
    
    if not pages:
        print("❌ No pages found in database")
        sys.exit(1)
    
    print(f"✓ Found {len(pages)} pages")
    
    # Clean and format pages
    print("\n3. Cleaning wiki content...")
    chatbot_temp = WikiChatbot.__new__(WikiChatbot)  # Create instance without __init__
    
    formatted_pages = []
    for page in pages:
        # Handle bytes
        page_title = page['page_title']
        if isinstance(page_title, bytes):
            page_title = page_title.decode('utf-8', errors='ignore')
        page_title = page_title.replace('_', ' ')
        
        # Get full content for this page
        full_page = db.get_page_by_title(page_title)
        if not full_page:
            continue
        
        content = full_page.get('content', '')
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        
        # Clean wiki markup
        content = chatbot_temp.clean_wiki_text(content)
        
        formatted_pages.append({
            'page_id': page['page_id'],
            'title': page_title,
            'content': content
        })
    
    print(f"✓ Cleaned {len(formatted_pages)} pages")
    
    # Initialize vector store
    print("\n4. Initializing vector store...")
    vector_store = VectorStore()
    if not vector_store.initialize():
        print("❌ Failed to initialize vector store")
        sys.exit(1)
    
    # Clear existing data (optional - comment out to keep existing)
    if vector_store.collection.count() > 0:
        response = input(f"\nVector store already contains {vector_store.collection.count()} documents. Clear and re-index? (y/n): ")
        if response.lower() == 'y':
            vector_store.clear()
    
    # Index pages
    print("\n5. Indexing pages into vector database...")
    vector_store.index_pages(formatted_pages)
    
    # Show stats
    print("\n" + "=" * 60)
    stats = vector_store.get_stats()
    print("✓ Indexing Complete!")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Storage location: {stats['persist_directory']}")
    print("=" * 60)
    
    # Cleanup
    db.disconnect()
    print("\nYou can now use the chatbot with vector search enabled!")

if __name__ == "__main__":
    main()
