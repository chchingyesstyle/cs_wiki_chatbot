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
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 1024))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.5))
    
    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Web server settings
    WEB_SERVER_PORT = int(os.getenv('WEB_SERVER_PORT', 8080))
    
    # Vector store settings
    USE_VECTOR_SEARCH = os.getenv('USE_VECTOR_SEARCH', 'True').lower() == 'true'
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    VECTOR_TOP_K = int(os.getenv('VECTOR_TOP_K', 5))
    
    # Wiki settings
    WIKI_BASE_URL = os.getenv('WIKI_BASE_URL', 'http://172.17.7.95/cswikiuat/index.php')
