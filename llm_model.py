try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Running in test mode.")

from typing import Optional
from config import Config

class LlamaModel:
    """Wrapper for llama-cpp-python model"""
    
    def __init__(self):
        self.config = Config()
        self.model = None
    
    def load_model(self):
        """Load the GGUF model"""
        if not LLAMA_AVAILABLE:
            print("⚠️  Running in TEST MODE (llama-cpp-python not installed)")
            print("   Install with: pip install llama-cpp-python")
            return True
        
        try:
            print(f"Loading model from: {self.config.MODEL_PATH}")
            self.model = Llama(
                model_path=self.config.MODEL_PATH,
                n_ctx=self.config.MODEL_N_CTX,
                n_threads=self.config.MODEL_N_THREADS,
                verbose=False
            )
            print("Model loaded successfully")
            return True
        except Exception as e:
            print(f"Model loading error: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate response from the model"""
        if not LLAMA_AVAILABLE:
            return "[TEST MODE] This is a test response. Install llama-cpp-python and download a model to get real AI responses."
        
        if not self.model:
            return "Error: Model not loaded"
        
        try:
            max_tokens = max_tokens or self.config.MODEL_MAX_TOKENS
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=self.config.MODEL_TEMPERATURE,
                stop=["</s>", "User:", "\n\n\n"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Generation error: {e}")
            return f"Error generating response: {str(e)}"
