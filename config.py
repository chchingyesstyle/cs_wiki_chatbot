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
    
    # Llama model settings
    MODEL_PATH = os.getenv('MODEL_PATH', './models/model.gguf')
    MODEL_N_CTX = int(os.getenv('MODEL_N_CTX', 2048))
    MODEL_N_THREADS = int(os.getenv('MODEL_N_THREADS', 4))
    MODEL_MAX_TOKENS = int(os.getenv('MODEL_MAX_TOKENS', 512))
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', 0.7))
    
    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Vector store settings
    USE_VECTOR_SEARCH = os.getenv('USE_VECTOR_SEARCH', 'True').lower() == 'true'
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    VECTOR_TOP_K = int(os.getenv('VECTOR_TOP_K', 3))
