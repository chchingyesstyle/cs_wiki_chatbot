from db_connector import WikiDBConnector
from llm_model import LlamaModel
from typing import Dict, List
import re

class WikiChatbot:
    """Main chatbot logic combining wiki data and LLM"""
    
    def __init__(self):
        self.db = WikiDBConnector()
        self.llm = LlamaModel()
        self.db.connect()
        self.llm.load_model()
    
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
    
    def retrieve_context(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Retrieve relevant wiki pages for the query"""
        results = self.db.search_pages(query, limit=max_pages)
        
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
        """Build the prompt for the LLM with wiki context"""
        
        # Build context section
        context_text = ""
        if context_pages:
            context_text = "Here is relevant information from the wiki:\n\n"
            for i, page in enumerate(context_pages, 1):
                context_text += f"[Page {i}: {page['title']}]\n{page['content']}\n\n"
        
        # Build full prompt
        prompt = f"""You are a helpful assistant that answers questions based on a wiki knowledge base.

{context_text}

User question: {user_question}

Based on the wiki information provided above, please answer the question. If the information is not available in the wiki pages, say so clearly.

Answer:"""
        
        return prompt
    
    def chat(self, user_question: str) -> Dict:
        """Main chat function"""
        
        # Retrieve relevant wiki pages
        context_pages = self.retrieve_context(user_question, max_pages=3)
        
        # Build prompt
        prompt = self.build_prompt(user_question, context_pages)
        
        # Generate response
        answer = self.llm.generate_response(prompt)
        
        return {
            'question': user_question,
            'answer': answer,
            'sources': [page['title'] for page in context_pages],
            'context_used': len(context_pages) > 0
        }
    
    def close(self):
        """Clean up resources"""
        self.db.disconnect()
