"""
Feedback Storage System using ChromaDB for CS Wiki Chatbot

Stores user ratings and corrections in ChromaDB for:
1. Manual review and improvement
2. Semantic search for similar Q&A pairs
3. Future prompt enhancement with good Q&A examples
4. Potential fine-tuning data collection

Uses the same ChromaDB instance as the vector store for consistency.
"""

import chromadb
from chromadb.utils import embedding_functions
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class FeedbackStore:
    """Store and retrieve user feedback on chatbot responses using ChromaDB"""
    
    def __init__(self, persist_directory: str = None):
        # Use same directory as vector store or configurable path
        self.persist_directory = persist_directory or os.environ.get('VECTOR_DB_PATH', './chroma_db')
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize ChromaDB client and feedback collection"""
        try:
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Use same embedding model as wiki pages for consistency
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create feedback collection (separate from wiki_pages)
            self.collection = self.client.get_or_create_collection(
                name="user_feedback",
                embedding_function=self.embedding_function,
                metadata={"description": "User feedback on chatbot responses"}
            )
            
            self._initialized = True
            print(f"✓ Feedback store initialized with {self.collection.count()} entries")
            return True
            
        except Exception as e:
            print(f"❌ Feedback store initialization error: {e}")
            return False
    
    def save_feedback(self, 
                      question: str,
                      answer: str,
                      rating: str,
                      sources: List[Dict] = None,
                      correction: str = None,
                      user_comment: str = None,
                      session_id: str = None,
                      retrieval_method: str = None) -> str:
        """
        Save user feedback to ChromaDB
        
        Args:
            question: Original user question
            answer: Chatbot's answer
            rating: 'up' (thumbs up) or 'down' (thumbs down)
            sources: List of source documents used
            correction: User-provided correct answer (optional)
            user_comment: Additional user feedback (optional)
            session_id: Session identifier for grouping (optional)
            retrieval_method: 'vector_search' or 'keyword_search'
            
        Returns:
            Feedback ID (UUID string)
        """
        if not self._initialized:
            if not self.initialize():
                raise Exception("Feedback store not initialized")
        
        try:
            feedback_id = str(uuid.uuid4())
            
            # Create document text for embedding (question + answer for semantic search)
            document_text = f"Question: {question}\nAnswer: {answer}"
            if correction:
                document_text += f"\nCorrection: {correction}"
            
            # Store metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'question': question[:500],  # ChromaDB has metadata size limits
                'answer': answer[:2000],
                'rating': rating,
                'reviewed': 'false',
                'retrieval_method': retrieval_method or 'unknown'
            }
            
            # Add optional fields
            if sources:
                metadata['sources'] = json.dumps(sources)[:1000]
            if correction:
                metadata['correction'] = correction[:2000]
            if user_comment:
                metadata['user_comment'] = user_comment[:500]
            if session_id:
                metadata['session_id'] = session_id
            
            # Add to collection
            self.collection.add(
                ids=[feedback_id],
                documents=[document_text],
                metadatas=[metadata]
            )
            
            print(f"✓ Feedback saved (ID: {feedback_id[:8]}..., Rating: {rating})")
            return feedback_id
            
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
            raise
    
    def get_feedback(self, 
                     rating: str = None,
                     reviewed: bool = None,
                     limit: int = 100) -> List[Dict]:
        """
        Retrieve feedback entries with optional filters
        
        Args:
            rating: Filter by 'up' or 'down' (optional)
            reviewed: Filter by reviewed status (optional)
            limit: Maximum number of results
            
        Returns:
            List of feedback entries
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            # Build where clause for filtering
            where_clause = {}
            if rating:
                where_clause['rating'] = rating
            if reviewed is not None:
                where_clause['reviewed'] = 'true' if reviewed else 'false'
            
            # Get all entries (ChromaDB doesn't have great filtering, so we filter in memory)
            if where_clause:
                results = self.collection.get(
                    where=where_clause if len(where_clause) == 1 else {"$and": [{k: v} for k, v in where_clause.items()]},
                    limit=limit,
                    include=['metadatas', 'documents']
                )
            else:
                results = self.collection.get(
                    limit=limit,
                    include=['metadatas', 'documents']
                )
            
            feedback_list = []
            if results['ids']:
                for i, feedback_id in enumerate(results['ids']):
                    entry = {
                        'id': feedback_id,
                        'document': results['documents'][i] if results['documents'] else None,
                        **results['metadatas'][i]
                    }
                    # Parse sources JSON
                    if entry.get('sources'):
                        try:
                            entry['sources'] = json.loads(entry['sources'])
                        except:
                            pass
                    feedback_list.append(entry)
            
            # Sort by timestamp descending
            feedback_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return feedback_list
            
        except Exception as e:
            print(f"❌ Error retrieving feedback: {e}")
            return []
    
    def search_similar_feedback(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar Q&A pairs using semantic search
        
        Useful for:
        - Finding if similar questions were asked before
        - Finding good answers to use as few-shot examples
        - Identifying patterns in negative feedback
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )
            
            similar = []
            if results['ids'] and results['ids'][0]:
                for i, feedback_id in enumerate(results['ids'][0]):
                    entry = {
                        'id': feedback_id,
                        'document': results['documents'][0][i],
                        'similarity': 1 - results['distances'][0][i],
                        **results['metadatas'][0][i]
                    }
                    if entry.get('sources'):
                        try:
                            entry['sources'] = json.loads(entry['sources'])
                        except:
                            pass
                    similar.append(entry)
            
            return similar
            
        except Exception as e:
            print(f"❌ Error searching feedback: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get feedback statistics"""
        if not self._initialized:
            if not self.initialize():
                return {'error': 'Not initialized'}
        
        try:
            total = self.collection.count()
            
            # Get counts by rating
            up_results = self.collection.get(where={'rating': 'up'}, include=[])
            thumbs_up = len(up_results['ids']) if up_results['ids'] else 0
            
            down_results = self.collection.get(where={'rating': 'down'}, include=[])
            thumbs_down = len(down_results['ids']) if down_results['ids'] else 0
            
            pending_results = self.collection.get(where={'reviewed': 'false'}, include=[])
            pending_review = len(pending_results['ids']) if pending_results['ids'] else 0
            
            return {
                'total': total,
                'thumbs_up': thumbs_up,
                'thumbs_down': thumbs_down,
                'pending_review': pending_review,
                'satisfaction_rate': round(thumbs_up / total * 100, 1) if total > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {'error': str(e)}
    
    def mark_reviewed(self, feedback_id: str, reviewer_notes: str = None) -> bool:
        """Mark a feedback entry as reviewed"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            # Update metadata
            update_metadata = {
                'reviewed': 'true',
                'reviewed_at': datetime.now().isoformat()
            }
            if reviewer_notes:
                update_metadata['reviewer_notes'] = reviewer_notes[:500]
            
            self.collection.update(
                ids=[feedback_id],
                metadatas=[update_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error marking as reviewed: {e}")
            return False
    
    def get_training_data(self, only_positive: bool = True) -> List[Dict]:
        """
        Export feedback for potential fine-tuning or few-shot prompts
        
        Returns Q&A pairs formatted for training:
        - Positive ratings with original answers
        - Negative ratings with corrections (if provided)
        """
        if not self._initialized:
            if not self.initialize():
                return []
        
        try:
            training_data = []
            
            # Get positive feedback
            positive = self.collection.get(
                where={'rating': 'up'},
                include=['metadatas']
            )
            
            if positive['ids']:
                for i, _ in enumerate(positive['ids']):
                    meta = positive['metadatas'][i]
                    training_data.append({
                        'question': meta.get('question'),
                        'answer': meta.get('answer'),
                        'rating': 'up'
                    })
            
            # Get negative feedback with corrections
            if not only_positive:
                negative = self.collection.get(
                    where={'rating': 'down'},
                    include=['metadatas']
                )
                
                if negative['ids']:
                    for i, _ in enumerate(negative['ids']):
                        meta = negative['metadatas'][i]
                        if meta.get('correction'):
                            training_data.append({
                                'question': meta.get('question'),
                                'answer': meta.get('correction'),  # Use correction as correct answer
                                'rating': 'corrected'
                            })
            
            return training_data
            
        except Exception as e:
            print(f"❌ Error exporting training data: {e}")
            return []
    
    def delete_feedback(self, feedback_id: str) -> bool:
        """Delete a feedback entry"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        try:
            self.collection.delete(ids=[feedback_id])
            return True
        except Exception as e:
            print(f"❌ Error deleting feedback: {e}")
            return False


# Quick test
if __name__ == "__main__":
    store = FeedbackStore('./test_chroma_feedback')
    store.initialize()
    
    # Test save
    fid = store.save_feedback(
        question="How to return an order?",
        answer="To return an order, please contact customer service...",
        rating="up",
        sources=[{"title": "Returns Policy", "url": "http://wiki/Returns"}]
    )
    print(f"Saved feedback ID: {fid}")
    
    # Test stats
    stats = store.get_stats()
    print(f"Stats: {stats}")
    
    # Test search
    similar = store.search_similar_feedback("order returns")
    print(f"Similar feedback: {len(similar)} found")
    
    # Cleanup
    import shutil
    shutil.rmtree('./test_chroma_feedback', ignore_errors=True)
    print("Test completed!")
