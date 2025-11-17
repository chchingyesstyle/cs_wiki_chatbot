"""
Local LLM wrapper using llama-cpp-python
Supports GGUF format models like Llama-2-7B-Chat
"""
from llama_cpp import Llama
from typing import Optional
from config import Config
import os

class LLMModel:
    """Wrapper for local LLM using llama-cpp-python"""
    
    def __init__(self):
        self.config = Config()
        self.llm = None
    
    def load_model(self):
        """Load the local GGUF model"""
        try:
            model_path = self.config.MODEL_PATH
            
            if not model_path:
                print("⚠️  Warning: MODEL_PATH not set in .env file")
                return False
            
            if not os.path.exists(model_path):
                print(f"⚠️  Warning: Model file not found at {model_path}")
                return False
            
            print(f"Loading model from {model_path}...")
            print("This may take a few minutes on first load...")
            
            self.llm = Llama(
                model_path=model_path,
                n_ctx=self.config.MODEL_CONTEXT_LENGTH,
                n_threads=self.config.MODEL_THREADS,
                n_gpu_layers=self.config.MODEL_GPU_LAYERS,
                verbose=False
            )
            
            print(f"✓ Local LLM loaded successfully")
            print(f"  Model: {os.path.basename(model_path)}")
            print(f"  Context length: {self.config.MODEL_CONTEXT_LENGTH}")
            print(f"  Threads: {self.config.MODEL_THREADS}")
            print(f"  GPU layers: {self.config.MODEL_GPU_LAYERS}")
            return True
            
        except Exception as e:
            print(f"Model loading error: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response using local LLM"""
        if not self.llm:
            return "Error: Local LLM not loaded"
        
        try:
            max_tokens = max_tokens or self.config.MODEL_MAX_TOKENS
            
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=self.config.MODEL_TEMPERATURE,
                top_p=self.config.MODEL_TOP_P,
                stop=["USER:", "QUESTION:", "\n\n\n"],
                echo=False
            )
            
            generated_text = response['choices'][0]['text'].strip()
            return generated_text
            
        except Exception as e:
            print(f"Generation error: {e}")
            return f"Error generating response: {str(e)}"
