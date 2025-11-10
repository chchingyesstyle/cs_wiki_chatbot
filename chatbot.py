"""
MediaWiki RAG (Retrieval-Augmented Generation) Chatbot

RAG Architecture:
1. RETRIEVAL: Find relevant wiki pages using vector/keyword search
2. AUGMENTATION: Build context-enriched prompt with retrieved documents
3. GENERATION: Generate answer using LLM with customer service persona

Customer Service Agent Persona:
- Answers based ONLY on provided context
- Cites sources explicitly using **Source: [Name]** format
- Says "I don't know" when context lacks information
- Never makes up information outside the context
"""

from db_connector import WikiDBConnector
from llm_model import LlamaModel
from vector_store import VectorStore
from config import Config
from typing import Dict, List
import re

class WikiChatbot:
    """Main chatbot logic combining wiki data and LLM"""
    
    def __init__(self):
        self.config = Config()
        self.db = WikiDBConnector()
        self.llm = LlamaModel()
        self.vector_store = None
        
        self.db.connect()
        self.llm.load_model()
        
        # Initialize vector store if enabled
        if self.config.USE_VECTOR_SEARCH:
            try:
                self.vector_store = VectorStore(persist_directory=self.config.VECTOR_DB_PATH)
                if self.vector_store.initialize():
                    if not self.vector_store.is_empty():
                        print(f"✓ Vector search enabled ({self.vector_store.collection.count()} documents)")
                    else:
                        print("⚠️  Vector store is empty. Run index_wiki.py to populate it.")
                        self.vector_store = None
                else:
                    print("⚠️  Vector store initialization failed. Using keyword search only.")
                    self.vector_store = None
            except Exception as e:
                print(f"⚠️  Vector store error: {e}. Using keyword search only.")
                self.vector_store = None
    
    def clean_wiki_text(self, text: str) -> str:
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
    
    def extract_keywords(self, query: str) -> str:
        """Extract important keywords from user query"""
        # Remove common question words but keep important abbreviations
        stop_words = ['what', 'is', 'are', 'the', 'how', 'can', 'do', 'does', 'tell', 'me', 'about', 'please']
        
        # Handle domain names specially (keep .com, .net, etc.)
        # Replace periods in domain names with placeholder, then remove other punctuation
        import re
        # Find domain-like patterns (word.com, word.net, etc.)
        query_processed = re.sub(r'\.com\b', 'DOTCOM', query, flags=re.IGNORECASE)
        query_processed = re.sub(r'\.net\b', 'DOTNET', query_processed, flags=re.IGNORECASE)
        query_processed = re.sub(r'\.org\b', 'DOTORG', query_processed, flags=re.IGNORECASE)
        
        # Remove other punctuation
        query_processed = query_processed.replace('?', '').replace(',', '').replace('.', '')
        
        # Restore domain names
        query_processed = query_processed.replace('DOTCOM', '.com')
        query_processed = query_processed.replace('DOTNET', '.net')
        query_processed = query_processed.replace('DOTORG', '.org')
        
        words = query_processed.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        return ' '.join(keywords[:6])  # Limit to top 6 keywords
    
    def retrieve_context(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Retrieve relevant wiki pages for the query"""
        
        # Use vector search if available
        if self.vector_store:
            return self._retrieve_context_vector(query, max_pages)
        else:
            return self._retrieve_context_keyword(query, max_pages)
    
    def _retrieve_context_vector(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Retrieve context using vector/semantic search"""
        try:
            # Search vector store
            vector_results = self.vector_store.search(query, top_k=max_pages)
            
            context_pages = []
            for result in vector_results:
                # Get full page content from database
                page_data = self.db.get_page_by_title(result['title'].replace(' ', '_'))
                
                if page_data:
                    content = page_data.get('content', '')
                    if isinstance(content, bytes):
                        content = content.decode('utf-8', errors='ignore')
                    content = self.clean_wiki_text(content)
                    
                    # Limit content length
                    if len(content) > 1500:
                        content = content[:1500] + "..."
                    
                    context_pages.append({
                        'title': result['title'],
                        'content': content,
                        'similarity': result.get('similarity_score')
                    })
            
            return context_pages
            
        except Exception as e:
            print(f"Vector search error: {e}. Falling back to keyword search.")
            return self._retrieve_context_keyword(query, max_pages)
    
    def _retrieve_context_keyword(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Retrieve context using keyword search"""
        # Extract keywords from the question
        keywords = self.extract_keywords(query)
        
        # Try searching with all keywords first
        results = self.db.search_pages(keywords, limit=max_pages)
        
        # If no results, try with fewer keywords (progressively)
        if not results and len(keywords.split()) > 2:
            # Try first 3 keywords
            keywords_reduced = ' '.join(keywords.split()[:3])
            results = self.db.search_pages(keywords_reduced, limit=max_pages)
            
            # Try first 2 keywords
            if not results and len(keywords.split()) > 1:
                keywords_reduced = ' '.join(keywords.split()[:2])
                results = self.db.search_pages(keywords_reduced, limit=max_pages)
        
        # If still no results, try each keyword individually (prioritize longer keywords first)
        if not results:
            sorted_keywords = sorted(keywords.split(), key=len, reverse=True)
            for keyword in sorted_keywords[:4]:
                if len(keyword) >= 2:  # Allow 2-char keywords like "BE"
                    results = self.db.search_pages(keyword, limit=max_pages)
                    if results:
                        break
        
        context_pages = []
        for result in results:
            # Handle bytes from database
            page_title = result['page_title']
            if isinstance(page_title, bytes):
                page_title = page_title.decode('utf-8', errors='ignore')
            page_title = page_title.replace('_', ' ')
            
            content = result.get('content', '')
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            content = self.clean_wiki_text(content)
            
            # Limit content length to avoid context overflow
            if len(content) > 1500:
                content = content[:1500] + "..."
            
            context_pages.append({
                'title': page_title,
                'content': content
            })
        
        return context_pages
    
    def build_prompt(self, user_question: str, context_pages: List[Dict]) -> str:
        """Build RAG prompt for customer service agent"""
        
        # Build context section with clear source references
        context_text = ""
        if context_pages:
            context_text = "CONTEXT INFORMATION:\n"
            for i, page in enumerate(context_pages, 1):
                context_text += f"\n[Source {i}: {page['title']}]\n{page['content']}\n"
        else:
            context_text = "CONTEXT INFORMATION:\nNo relevant information found.\n"
        
        # Build RAG prompt with strict instructions
        prompt = f"""You are a customer service agent that answers questions based ONLY on the provided context.

{context_text}

INSTRUCTIONS:
- Answer based ONLY on the context provided above
- If the context contains the answer, provide a clear and helpful response
- You MUST cite sources at the end using format: **Source: [Source Name]**
- If multiple sources are used, list all: **Sources: [Source 1], [Source 2]**
- If the context does not contain enough information to answer, respond with: "I don't know based on the available information."
- Do not make up information or use knowledge outside the provided context

USER QUESTION: {user_question}

ANSWER:"""
        
        return prompt
    
    def chat(self, user_question: str) -> Dict:
        """Main RAG chat function with retrieval and generation"""
        
        # Step 1: Retrieve relevant wiki pages (Retrieval)
        context_pages = self.retrieve_context(user_question, max_pages=3)
        
        # Step 2: Build RAG prompt with context (Augmentation)
        prompt = self.build_prompt(user_question, context_pages)
        
        # Step 3: Generate response from LLM (Generation)
        answer = self.llm.generate_response(prompt)
        
        # Step 4: Extract and format sources
        sources = [page['title'] for page in context_pages]
        
        # Add metadata about retrieval method used
        retrieval_method = "vector_search" if self.vector_store else "keyword_search"
        
        return {
            'question': user_question,
            'answer': answer,
            'sources': sources,
            'context_used': len(context_pages) > 0,
            'retrieval_method': retrieval_method,
            'num_sources': len(sources)
        }
    
    def close(self):
        """Clean up resources"""
        self.db.disconnect()
