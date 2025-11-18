import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'wikidb')
    DB_USER = os.getenv('DB_USER', 'wikiuser')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Local LLM settings
    MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/llama-2-7b-chat.Q4_K_M.gguf')
    MODEL_CONTEXT_LENGTH = int(os.getenv('MODEL_CONTEXT_LENGTH', 4096))
    MODEL_MAX_TOKENS = int(os.getenv('MODEL_MAX_TOKENS', 512))
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.3))
    MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', 0.9))
    MODEL_THREADS = int(os.getenv('MODEL_THREADS', 4))
    MODEL_GPU_LAYERS = int(os.getenv('MODEL_GPU_LAYERS', 0))
    
    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Web server settings
    WEB_SERVER_PORT = int(os.getenv('WEB_SERVER_PORT', 8080))
    
    # Vector store settings
    USE_VECTOR_SEARCH = os.getenv('USE_VECTOR_SEARCH', 'True').lower() == 'true'
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    VECTOR_TOP_K = int(os.getenv('VECTOR_TOP_K', 3))
    
    # Wiki settings
    WIKI_BASE_URL = os.getenv('WIKI_BASE_URL', 'http://172.17.7.95/cswikiuat/index.php')
