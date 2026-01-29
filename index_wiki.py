#!/usr/bin/env python3
"""
Script to index MediaWiki pages into vector database
Run this once to populate the vector store, or when wiki content changes

Can be run as:
1. CLI: python index_wiki.py
2. API: POST /api/reindex
"""

from db_connector import WikiDBConnector
from vector_store import VectorStore
import sys
import re


def clean_wiki_text(text: str) -> str:
    """Remove MediaWiki markup for cleaner context"""
    if not text:
        return ""
    
    # Remove common wiki markup
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', text)  # [[link|text]] -> text
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # [[link]] -> link
    text = re.sub(r'\{\{[^\}]+\}\}', '', text)  # Remove templates
    text = re.sub(r'==+\s*([^=]+)\s*==+', r'\1:', text)  # Headers
    text = re.sub(r"'''([^']+)'''", r'\1', text)  # Bold
    text = re.sub(r"''([^']+)''", r'\1', text)  # Italic
    text = re.sub(r'<[^>]+>', '', text)  # HTML tags
    text = re.sub(r'\n\n+', '\n\n', text)  # Multiple newlines
    
    return text.strip()


def reindex_wiki(clear_existing: bool = True, persist_directory: str = None) -> dict:
    """
    Reindex all wiki pages into vector database.
    
    Args:
        clear_existing: If True, clears existing vectors before indexing
        persist_directory: Optional custom path for vector store
        
    Returns:
        dict with status, pages_found, pages_indexed, and any errors
    """
    result = {
        'success': False,
        'pages_found': 0,
        'pages_indexed': 0,
        'pages_skipped': 0,
        'message': '',
        'errors': []
    }
    
    db = None
    
    try:
        # Step 1: Connect to database
        db = WikiDBConnector()
        if not db.connect():
            result['errors'].append('Failed to connect to database')
            result['message'] = 'Database connection failed'
            return result
        
        # Step 2: Fetch all pages
        pages = db.get_all_pages(limit=10000)
        
        if not pages:
            result['errors'].append('No pages found in database')
            result['message'] = 'No wiki pages found'
            return result
        
        result['pages_found'] = len(pages)
        
        # Step 3: Clean and format pages
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

            # Skip redirect pages and pages with no useful content
            if content.strip().startswith('#REDIRECT') or len(content.strip()) < 50:
                result['pages_skipped'] += 1
                continue

            # Skip outdated, expired, or moved pages
            title_upper = page_title.upper()
            if any(marker in title_upper for marker in ['(OUTDATED)', '(EXPIRED)', '(MOVED)']):
                result['pages_skipped'] += 1
                continue

            # Clean wiki markup
            content = clean_wiki_text(content)

            # Skip if cleaned content is too short
            if len(content.strip()) < 50:
                result['pages_skipped'] += 1
                continue

            formatted_pages.append({
                'page_id': page['page_id'],
                'title': page_title,
                'content': content
            })
        
        # Step 4: Initialize vector store
        from config import Config
        config = Config()
        vector_store = VectorStore(persist_directory=persist_directory or config.VECTOR_DB_PATH)
        
        if not vector_store.initialize():
            result['errors'].append('Failed to initialize vector store')
            result['message'] = 'Vector store initialization failed'
            return result
        
        # Step 5: Clear existing if requested
        if clear_existing and vector_store.collection.count() > 0:
            vector_store.clear()
        
        # Step 6: Index pages
        vector_store.index_pages(formatted_pages)
        
        result['pages_indexed'] = len(formatted_pages)
        result['success'] = True
        result['message'] = f'Successfully indexed {len(formatted_pages)} pages'
        
    except Exception as e:
        result['errors'].append(str(e))
        result['message'] = f'Indexing failed: {str(e)}'
        
    finally:
        if db:
            db.disconnect()
    
    return result


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

        # Skip redirect pages and pages with no useful content
        if content.strip().startswith('#REDIRECT') or len(content.strip()) < 50:
            continue

        # Skip outdated, expired, or moved pages (unless they're the only version)
        title_upper = page_title.upper()
        if any(marker in title_upper for marker in ['(OUTDATED)', '(EXPIRED)', '(MOVED)']):
            continue

        # Clean wiki markup
        content = clean_wiki_text(content)

        # Skip if cleaned content is too short (likely no useful info)
        if len(content.strip()) < 50:
            continue

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
