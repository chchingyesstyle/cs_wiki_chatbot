"""
OpenAI API wrapper for chat completions
"""
from openai import OpenAI
from typing import Optional
from config import Config

class OpenAIModel:
    """Wrapper for OpenAI API"""
    
    def __init__(self):
        self.config = Config()
        self.client = None
    
    def load_model(self):
        """Initialize OpenAI client"""
        try:
            if not self.config.OPENAI_API_KEY:
                print("⚠️  Warning: OPENAI_API_KEY not set in .env file")
                return False
            
            self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            print(f"✓ OpenAI client initialized (model: {self.config.OPENAI_MODEL})")
            return True
        except Exception as e:
            print(f"OpenAI client initialization error: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response using OpenAI API"""
        if not self.client:
            return "Error: OpenAI client not initialized"
        
        try:
            max_tokens = max_tokens or self.config.OPENAI_MAX_TOKENS
            
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.config.OPENAI_TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return f"Error generating response: {str(e)}"
