import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import os
import json

class VectorStore:
    """Vector database for semantic search of wiki content"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_function = None
        
    def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Use sentence-transformers for embeddings (all-MiniLM-L6-v2 is fast and good)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="wiki_pages",
                embedding_function=self.embedding_function,
                metadata={"description": "MediaWiki pages for semantic search"}
            )
            
            print(f"✓ Vector store initialized with {self.collection.count()} documents")
            return True
            
        except Exception as e:
            print(f"Vector store initialization error: {e}")
            return False
    
    def index_pages(self, pages: List[Dict], batch_size: int = 100):
        """Index wiki pages into vector database"""
        if not self.collection:
            raise Exception("Vector store not initialized")
        
        total_pages = len(pages)
        print(f"Indexing {total_pages} pages into vector database...")
        
        # Process in batches for better performance
        for i in range(0, total_pages, batch_size):
            batch = pages[i:i + batch_size]
            
            ids = []
            documents = []
            metadatas = []
            
            for page in batch:
                page_id = str(page['page_id'])
                title = page['title']
                content = page['content']
                
                # Combine title and content for better semantic search
                # Weight title more heavily by repeating it
                combined_text = f"{title}. {title}. {content}"
                
                ids.append(page_id)
                documents.append(combined_text)
                metadatas.append({
                    'page_id': page['page_id'],
                    'title': title,
                    'content_length': len(content)
                })
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"  Indexed {min(i + batch_size, total_pages)}/{total_pages} pages")
        
        print(f"✓ Indexing complete! Total documents: {self.collection.count()}")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Semantic search for relevant wiki pages"""
        if not self.collection:
            raise Exception("Vector store not initialized")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=['metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, page_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else None
                    
                    formatted_results.append({
                        'page_id': metadata['page_id'],
                        'title': metadata['title'],
                        'similarity_score': 1 - distance if distance else None  # Convert distance to similarity
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    def clear(self):
        """Clear all documents from the collection"""
        if self.collection:
            self.client.delete_collection("wiki_pages")
            self.collection = self.client.create_collection(
                name="wiki_pages",
                embedding_function=self.embedding_function
            )
            print("Vector store cleared")
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        if not self.collection:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'ready',
            'total_documents': self.collection.count(),
            'persist_directory': self.persist_directory
        }
    
    def is_empty(self) -> bool:
        """Check if vector store is empty"""
        if not self.collection:
            return True
        return self.collection.count() == 0
