import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://ollama:11434')
    
    # Models
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'Qwen/Qwen3-Embedding-0.6B')
    LLM_MODEL = os.getenv('LLM_MODEL', 'llama3.2:latest')
    
    # Database
    VECTOR_TABLE_NAME = os.getenv('VECTOR_TABLE_NAME', 'documents')
    MATCH_THRESHOLD = float(os.getenv('MATCH_THRESHOLD', '0.7'))
    MATCH_COUNT = int(os.getenv('MATCH_COUNT', '3'))
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    PORT = int(os.getenv('PORT', '5000'))
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        required = [
            ('SUPABASE_URL', Config.SUPABASE_URL),
            ('SUPABASE_KEY', Config.SUPABASE_KEY),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please check your .env file."
            )