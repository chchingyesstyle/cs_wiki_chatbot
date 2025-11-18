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
    
    # Clean and format pages WITH CHUNKING
    print("\n3. Cleaning and chunking wiki content...")
    chatbot_temp = WikiChatbot.__new__(WikiChatbot)  # Create instance without __init__
    
    chunk_size = 1800  # Characters per chunk
    chunk_overlap = 300  # Overlap between chunks to avoid cutting sentences
    
    formatted_pages = []
    total_chunks = 0
    
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

        # Skip redirect pages and pages with no useful content
        if content.strip().startswith('#REDIRECT') or len(content.strip()) < 50:
            continue

        # Skip outdated, expired, or moved pages (unless they're the only version)
        title_upper = page_title.upper()
        if any(marker in title_upper for marker in ['(OUTDATED)', '(EXPIRED)', '(MOVED)']):
            continue

        # Clean wiki markup
        content = chatbot_temp.clean_wiki_text(content)

        # Skip if cleaned content is too short (likely no useful info)
        if len(content.strip()) < 50:
            continue

        # Split long pages into chunks
        if len(content) <= chunk_size:
            # Short page - index as is
            formatted_pages.append({
                'page_id': f"{page['page_id']}_0",
                'title': page_title,
                'content': content
            })
            total_chunks += 1
        else:
            # Long page - split into chunks
            chunks_for_page = 0
            for i in range(0, len(content), chunk_size - chunk_overlap):
                chunk = content[i:i + chunk_size]
                
                # Skip very short end chunks
                if len(chunk.strip()) < 100:
                    continue
                
                # Create chunk title showing it's part of a page
                chunk_title = page_title
                if chunks_for_page > 0:
                    chunk_title = f"{page_title} (part {chunks_for_page + 1})"
                
                formatted_pages.append({
                    'page_id': f"{page['page_id']}_{chunks_for_page}",
                    'title': chunk_title,
                    'content': chunk
                })
                chunks_for_page += 1
                total_chunks += 1
    
    print(f"✓ Processed {len(pages)} pages into {total_chunks} chunks")
    print(f"  Average chunks per page: {total_chunks / len(formatted_pages) if formatted_pages else 0:.1f}")
    
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
