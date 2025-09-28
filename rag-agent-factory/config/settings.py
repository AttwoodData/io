"""
Configuration settings for RAG Agent Factory
Simple, readable configuration following project principles
"""

import os

class Config:
    """
    Basic configuration class
    Environment-based settings for different deployment scenarios
    """
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Ollama configuration
    OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'localhost')
    OLLAMA_PORT = os.environ.get('OLLAMA_PORT', '11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')
    
    # File upload settings (for future phases)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/app.log'
    
    @staticmethod
    def init_app(app):
        """
        Initialize application with configuration
        """
        # Create required directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('temp', exist_ok=True)
