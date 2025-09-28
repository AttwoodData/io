#!/bin/bash

# RAG Agent Factory - Phase 1 Repository Setup Script
# Creates complete directory structure and all necessary files

set -e  # Exit on any error

echo "🚀 Setting up RAG Agent Factory - Phase 1"
echo "========================================"

# Create main project directory
PROJECT_DIR="rag-agent-factory"
echo "📁 Creating project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Directory $PROJECT_DIR already exists. Remove it? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
        echo "🗑️  Removed existing directory"
    else
        echo "❌ Aborting setup"
        exit 1
    fi
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p config
mkdir -p llm
mkdir -p ui/components
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p utils
mkdir -p logs
mkdir -p temp
mkdir -p uploads

# Create __init__.py files
echo "🐍 Creating __init__.py files..."
touch config/__init__.py
touch llm/__init__.py
touch ui/__init__.py
touch ui/components/__init__.py
touch utils/__init__.py

# Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
EOF

# Create Dockerfile
echo "🐳 Creating Dockerfile..."
cat > Dockerfile << 'EOF'
# Multi-stage Dockerfile for RAG Agent Factory
# Stage 1: Build environment with all dependencies
FROM python:3.11-slim as builder

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    cmake \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel setuptools

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production runtime
FROM python:3.11-slim as production

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs /app/temp

# Copy application code
COPY . .

# Set permissions for uploads and temp directories
RUN chmod 755 /app/uploads /app/logs /app/temp

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Default command
CMD ["python", "app.py"]
EOF

# Create main app.py
echo "🌐 Creating app.py..."
cat > app.py << 'EOF'
"""
RAG Agent Factory - Phase 1: Simple Ollama Q&A
Main Flask application with minimal complexity and maximum readability.
"""

from flask import Flask, request, render_template, jsonify
import os
import logging
from datetime import datetime

# Import our modular components
from config.settings import Config
from llm.ollama_client import OllamaClient
from utils.error_handlers import handle_ollama_error, log_user_interaction

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Ollama client
ollama_client = OllamaClient()

@app.route('/')
def index():
    """
    Main page - simple question/answer interface
    Following project principle: simplicity over complexity
    """
    logger.info("User accessed main page")
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Handle question submission and return Ollama response
    Single question -> single answer (no conversation memory)
    """
    try:
        # Get question from form
        question = request.form.get('question', '').strip()
        
        if not question:
            return jsonify({
                'error': 'Please enter a question',
                'success': False
            }), 400
        
        # Log the interaction for Phase 1 tracking
        log_user_interaction(question, request.remote_addr)
        
        # Get response from Ollama
        logger.info(f"Processing question: {question[:50]}...")
        response = ollama_client.get_response(question)
        
        # Return JSON response for AJAX handling
        return jsonify({
            'question': question,
            'answer': response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return handle_ollama_error(e)

@app.route('/health')
def health_check():
    """
    Health check endpoint for Docker deployment
    """
    try:
        # Test Ollama connection
        test_response = ollama_client.test_connection()
        return jsonify({
            'status': 'healthy',
            'ollama_connected': test_response,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    logger.info("Starting RAG Agent Factory - Phase 1")
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Create config/settings.py
echo "⚙️  Creating config/settings.py..."
cat > config/settings.py << 'EOF'
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
EOF

# Create llm/ollama_client.py
echo "🤖 Creating llm/ollama_client.py..."
cat > llm/ollama_client.py << 'EOF'
"""
Ollama client for local LLM integration
Simple, reliable connection to local Ollama service
"""

import requests
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Simple Ollama client following project principle of simplicity over complexity
    Handles connection to local Ollama service with proper error handling
    """
    
    def __init__(self, host: str = 'localhost', port: str = '11434', model: str = 'llama3.2:3b'):
        """
        Initialize Ollama client with connection parameters
        
        Args:
            host: Ollama service host
            port: Ollama service port  
            model: Model name to use for generation
        """
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"
        
        logger.info(f"Initialized Ollama client: {self.base_url}, model: {model}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama service
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama connection test successful")
                return True
            else:
                logger.warning(f"Ollama connection test failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama connection test failed: {str(e)}")
            return False
    
    def get_response(self, question: str) -> str:
        """
        Get response from Ollama for a single question
        Phase 1: Simple question -> answer, no conversation memory
        
        Args:
            question: User question
            
        Returns:
            str: Ollama response
            
        Raises:
            Exception: If Ollama request fails
        """
        try:
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": question,
                "stream": False,  # Get complete response, not streaming
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 512  # Reasonable response length
                }
            }
            
            logger.info(f"Sending request to Ollama: {question[:50]}...")
            
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', 'No response received')
                
                logger.info(f"Received response from Ollama: {answer[:50]}...")
                return answer
                
            else:
                error_msg = f"Ollama request failed: HTTP {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "Ollama request timed out after 30 seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Ollama response: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def list_models(self) -> list:
        """
        Get list of available models from Ollama
        Useful for future phases and debugging
        
        Returns:
            list: Available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                models = [model['name'] for model in models_data.get('models', [])]
                logger.info(f"Available Ollama models: {models}")
                return models
            else:
                logger.warning(f"Failed to get model list: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get model list: {str(e)}")
            return []
EOF

# Create utils/error_handlers.py
echo "🛠️  Creating utils/error_handlers.py..."
cat > utils/error_handlers.py << 'EOF'
"""
Error handling utilities for RAG Agent Factory
Simple, consistent error handling following project principles
"""

import logging
from datetime import datetime
from flask import jsonify

logger = logging.getLogger(__name__)

def handle_ollama_error(error: Exception) -> tuple:
    """
    Handle Ollama-related errors with consistent formatting
    
    Args:
        error: Exception from Ollama interaction
        
    Returns:
        tuple: (JSON response, HTTP status code)
    """
    error_message = str(error)
    
    # Log the error for debugging
    logger.error(f"Ollama error: {error_message}")
    
    # Return user-friendly error response
    return jsonify({
        'error': 'Unable to process your question at this time. Please try again.',
        'technical_error': error_message,
        'success': False,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }), 500

def log_user_interaction(question: str, ip_address: str) -> None:
    """
    Log user interactions for Phase 1 tracking and debugging
    
    Args:
        question: User's question
        ip_address: User's IP address
    """
    logger.info(f"User interaction - IP: {ip_address}, Question: {question[:100]}...")
    
    # Simple file logging for Phase 1
    # Future phases will use more sophisticated tracking
    try:
        with open('logs/interactions.log', 'a') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"{timestamp},{ip_address},{question[:200]}\n")
    except Exception as e:
        logger.warning(f"Failed to log interaction: {str(e)}")

def validate_question(question: str) -> tuple:
    """
    Basic validation for user questions
    
    Args:
        question: User input to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not question:
        return False, "Question cannot be empty"
    
    if len(question.strip()) < 3:
        return False, "Question must be at least 3 characters long"
    
    if len(question) > 1000:
        return False, "Question must be less than 1000 characters"
    
    # Basic content filtering (can be expanded in future phases)
    forbidden_terms = ['<script>', '</script>', 'javascript:', 'eval(']
    for term in forbidden_terms:
        if term.lower() in question.lower():
            return False, "Question contains invalid content"
    
    return True, ""
EOF

# Create templates/base.html
echo "🎨 Creating templates/base.html..."
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}RAG Agent Factory{% endblock %}</title>
    
    <!-- Metropolis Font from Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Main CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header class="main-header">
        <div class="container">
            <h1 class="site-title">RAG Agent Factory</h1>
            <p class="site-subtitle">Phase 1: Simple Ollama Q&A</p>
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>

    <footer class="main-footer">
        <div class="container">
            <p>&copy; 2024 RAG Agent Factory | Built with simplicity and readability in mind</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
EOF

# Create templates/index.html
echo "🏠 Creating templates/index.html..."
cat > templates/index.html << 'EOF'
{% extends "base.html" %}

{% block title %}RAG Agent Factory - Ask a Question{% endblock %}

{% block content %}
<div class="qa-interface">
    <div class="question-section">
        <h2>Ask Ollama a Question</h2>
        <p class="instructions">
            Enter your question below and get an answer from our local Ollama model.
            This is Phase 1: Simple question → single answer (no conversation memory).
        </p>
        
        <form id="question-form" class="question-form">
            <div class="form-group">
                <label for="question" class="form-label">Your Question:</label>
                <textarea 
                    id="question" 
                    name="question" 
                    class="question-input" 
                    placeholder="What would you like to know?"
                    rows="4"
                    maxlength="1000"
                    required
                ></textarea>
                <div class="character-count">
                    <span id="char-count">0</span> / 1000 characters
                </div>
            </div>
            
            <button type="submit" id="submit-btn" class="submit-button">
                <span class="button-text">Ask Question</span>
                <span class="loading-spinner" style="display: none;">Processing...</span>
            </button>
        </form>
    </div>
    
    <div class="response-section" id="response-section" style="display: none;">
        <h3>Response:</h3>
        <div class="response-container">
            <div class="response-meta">
                <span class="timestamp" id="response-timestamp"></span>
                <span class="model-info">Model: Ollama (llama3.2:3b)</span>
            </div>
            <div class="response-content" id="response-content"></div>
        </div>
        
        <button type="button" id="ask-another" class="secondary-button">
            Ask Another Question
        </button>
    </div>
    
    <div class="error-section" id="error-section" style="display: none;">
        <h3>Error:</h3>
        <div class="error-container">
            <p class="error-message" id="error-message"></p>
            <button type="button" id="try-again" class="secondary-button">
                Try Again
            </button>
        </div>
    </div>
</div>

<!-- Status indicator -->
<div class="status-indicator" id="status-indicator">
    <div class="status-dot"></div>
    <span class="status-text">Checking Ollama connection...</span>
</div>
{% endblock %}
EOF

# Create static/css/main.css
echo "💄 Creating static/css/main.css..."
cat > static/css/main.css << 'EOF'
/* RAG Agent Factory - Main Stylesheet */
/* Following project principle: simplicity over complexity */

/* CSS Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', 'Metropolis', 'Arial', 'Helvetica', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    font-size: 16px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header Styles */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem 0;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.site-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.site-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    font-weight: 300;
}

/* Main Content */
.main-content {
    padding: 3rem 0;
    min-height: calc(100vh - 200px);
}

/* Q&A Interface */
.qa-interface {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    overflow: hidden;
}

.question-section {
    padding: 2rem;
    border-bottom: 1px solid #eee;
}

.question-section h2 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: #2d3748;
    font-weight: 600;
}

.instructions {
    color: #718096;
    margin-bottom: 2rem;
    font-size: 1rem;
    line-height: 1.6;
}

/* Form Styles */
.question-form {
    width: 100%;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #4a5568;
    font-size: 1rem;
}

.question-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.3s ease;
    line-height: 1.5;
}

.question-input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.character-count {
    text-align: right;
    font-size: 0.875rem;
    color: #a0aec0;
    margin-top: 0.5rem;
}

/* Button Styles */
.submit-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    min-width: 150px;
}

.submit-button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.submit-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.secondary-button {
    background: transparent;
    color: #667eea;
    border: 2px solid #667eea;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.secondary-button:hover {
    background: #667eea;
    color: white;
}

.loading-spinner {
    display: inline-block;
}

/* Response Section */
.response-section {
    padding: 2rem;
    background: #f7fafc;
}

.response-section h3 {
    color: #2d3748;
    margin-bottom: 1rem;
    font-size: 1.4rem;
    font-weight: 600;
}

.response-container {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid #48bb78;
}

.response-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e2e8f0;
    font-size: 0.875rem;
    color: #718096;
}

.response-content {
    color: #2d3748;
    line-height: 1.7;
    font-size: 1rem;
    white-space: pre-wrap;
}

/* Error Section */
.error-section {
    padding: 2rem;
    background: #fed7d7;
}

.error-section h3 {
    color: #c53030;
    margin-bottom: 1rem;
    font-size: 1.4rem;
    font-weight: 600;
}

.error-container {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid #e53e3e;
}

.error-message {
    color: #742a2a;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Status Indicator */
.status-indicator {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 50px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    z-index: 1000;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #fbbf24;
    animation: pulse 2s infinite;
}

.status-dot.connected {
    background: #10b981;
    animation: none;
}

.status-dot.error {
    background: #ef4444;
    animation: none;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Footer */
.main-footer {
    background: #2d3748;
    color: white;
    text-align: center;
    padding: 1.5rem 0;
    margin-top: 2rem;
}

.main-footer p {
    font-size: 0.875rem;
    opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 768px) {
    .site-title {
        font-size: 2rem;
    }
    
    .container {
        padding: 0 15px;
    }
    
    .qa-interface {
        margin: 1rem;
    }
    
    .question-section,
    .response-section,
    .error-section {
        padding: 1.5rem;
    }
    
    .response-meta {
        flex-direction: column;
        gap: 0.5rem;
        align-items: flex-start;
    }
    
    .status-indicator {
        bottom: 15px;
        right: 15px;
        padding: 0.75rem 1rem;
    }
}

@media (max-width: 480px) {
    .site-title {
        font-size: 1.75rem;
    }
    
    .question-section h2 {
        font-size: 1.5rem;
    }
    
    .submit-button {
        width: 100%;
        padding: 1.2rem;
    }
}
EOF

# Create static/js/main.js
echo "⚡ Creating static/js/main.js..."
cat > static/js/main.js << 'EOF'
// RAG Agent Factory - Main JavaScript
// Following project principle: simplicity over complexity

document.addEventListener('DOMContentLoaded', function() {
    console.log('RAG Agent Factory - Phase 1 loaded');
    
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Get DOM elements
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question');
    const submitBtn = document.getElementById('submit-btn');
    const responseSection = document.getElementById('response-section');
    const errorSection = document.getElementById('error-section');
    const statusIndicator = document.getElementById('status-indicator');
    
    // Initialize character counter
    initializeCharacterCounter();
    
    // Check Ollama connection status
    checkOllamaStatus();
    
    // Handle form submission
    if (questionForm) {
        questionForm.addEventListener('submit', handleQuestionSubmit);
    }
    
    // Handle "Ask Another Question" button
    const askAnotherBtn = document.getElementById('ask-another');
    if (askAnotherBtn) {
        askAnotherBtn.addEventListener('click', resetForm);
    }
    
    // Handle "Try Again" button
    const tryAgainBtn = document.getElementById('try-again');
    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', resetForm);
    }
}

function initializeCharacterCounter() {
    const questionInput = document.getElementById('question');
    const charCount = document.getElementById('char-count');
    
    if (questionInput && charCount) {
        questionInput.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCount.textContent = currentLength;
            
            // Change color as approaching limit
            if (currentLength > 800) {
                charCount.style.color = '#e53e3e';
            } else if (currentLength > 600) {
                charCount.style.color = '#dd6b20';
            } else {
                charCount.style.color = '#a0aec0';
            }
        });
    }
}

function checkOllamaStatus() {
    const statusIndicator = document.getElementById('status-indicator');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    // Check health endpoint
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'healthy' && data.ollama_connected) {
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Ollama connected';
                console.log('Ollama connection: OK');
            } else {
                statusDot.className = 'status-dot error';
                statusText.textContent = 'Ollama connection failed';
                console.warn('Ollama connection: Failed');
            }
        })
        .catch(error => {
            statusDot.className = 'status-dot error';
            statusText.textContent = 'System unavailable';
            console.error('Health check failed:', error);
        });
}

function handleQuestionSubmit(event) {
    event.preventDefault();
    
    const questionInput = document.getElementById('question');
    const question = questionInput.value.trim();
    
    // Basic validation
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    if (question.length < 3) {
        showError('Question must be at least 3 characters long');
        return;
    }
    
    if (question.length > 1000) {
        showError('Question must be less than 1000 characters');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    hideError();
    hideResponse();
    
    // Send question to server
    const formData = new FormData();
    formData.append('question', question);
    
    fetch('/ask', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        setLoadingState(false);
        
        if (data.success) {
            showResponse(data);
        } else {
            showError(data.error || 'An error occurred while processing your question');
        }
    })
    .catch(error => {
        setLoadingState(false);
        console.error('Error:', error);
        showError('Unable to connect to the server. Please try again.');
    });
}

function setLoadingState(isLoading) {
    const submitBtn = document.getElementById('submit-btn');
    const buttonText = submitBtn.querySelector('.button-text');
    const loadingSpinner = submitBtn.querySelector('.loading-spinner');
    
    if (isLoading) {
        submitBtn.disabled = true;
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'inline-block';
    } else {
        submitBtn.disabled = false;
        buttonText.style.display = 'inline-block';
        loadingSpinner.style.display = 'none';
    }
}

function showResponse(data) {
    const responseSection = document.getElementById('response-section');
    const responseContent = document.getElementById('response-content');
    const responseTimestamp = document.getElementById('response-timestamp');
    
    // Update content
    responseContent.textContent = data.answer;
    responseTimestamp.textContent = `Response generated at ${data.timestamp}`;
    
    // Show response section
    responseSection.style.display = 'block';
    
    // Scroll to response
    responseSection.scrollIntoView({ behavior: 'smooth' });
    
    console.log('Response displayed successfully');
}

function showError(message) {
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth' });
    
    console.error('Error displayed:', message);
}

function hideResponse() {
    const responseSection = document.getElementById('response-section');
    responseSection.style.display = 'none';
}

function hideError() {
    const errorSection = document.getElementById('error-section');
    errorSection.style.display = 'none';
}

function resetForm() {
    const questionInput = document.getElementById('question');
    const charCount = document.getElementById('char-count');
    
    // Reset form
    questionInput.value = '';
    charCount.textContent = '0';
    charCount.style.color = '#a0aec0';
    
    // Hide sections
    hideResponse();
    hideError();
    
    // Focus on input
    questionInput.focus();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    console.log('Form reset');
}

// Utility function for debugging
function logInteraction(action, data = {}) {
    console.log(`[RAG Factory] ${action}:`, data);
}

// Handle any uncaught errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    // Could send error reports to server in production
});
EOF

# Create .gitignore
echo "🚫 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/*.log
*.log

# Temporary files
temp/
tmp/
*.tmp

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment variables
.env
.env.local
.env.production

# Uploads
uploads/*
!uploads/.gitkeep

# Docker
.dockerignore

# Testing
.pytest_cache/
.coverage
htmlcov/

# Local development
local_config.py
EOF

# Create .dockerignore
echo "🐳 Creating .dockerignore..."
cat > .dockerignore << 'EOF'
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Documentation
README.md
docs/
*.md

# Development files
logs/
temp/
tmp/
uploads/

# Testing
tests/
.pytest_cache/

# Local development
local_config.py
.env.local
EOF

# Create development script
echo "🔧 Creating development script..."
cat > dev.sh << 'EOF'
#!/bin/bash

# RAG Agent Factory - Development Script
# Quick development workflow automation

echo "🚀 RAG Agent Factory - Development Workflow"
echo "==========================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if Ollama is running
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "⚠️  Ollama service not detected on localhost:11434"
        echo "   Make sure Ollama is running: ollama serve"
        echo "   Or update OLLAMA_HOST in config if running elsewhere"
    else
        echo "✅ Ollama service detected"
    fi
}

# Main development workflow
case "${1:-build}" in
    "build")
        echo "🔨 Building Docker image..."
        check_docker
        docker build -t rag-agent-factory .
        ;;
    "run")
        echo "🏃 Starting development container..."
        check_docker
        check_ollama
        docker rm -f rag-dev-container 2>/dev/null || true
        docker run -d -p 5001:5000 --name rag-dev-container --restart unless-stopped rag-agent-factory
        echo "✅ Container started at http://localhost:5001"
        echo "📊 View logs: ./dev.sh logs"
        ;;
    "deploy")
        echo "🚀 Full deployment (build + run)..."
        check_docker
        check_ollama
        docker rm -f rag-dev-container 2>/dev/null || true
        docker build -t rag-agent-factory .
        docker run -d -p 5001:5000 --name rag-dev-container --restart unless-stopped rag-agent-factory
        echo "✅ Deployment complete at http://localhost:5001"
        sleep 2
        echo "📋 Testing health endpoint..."
        curl -s http://localhost:5001/health | python3 -m json.tool || echo "Health check failed"
        ;;
    "logs")
        echo "📋 Viewing container logs..."
        docker logs -f rag-dev-container
        ;;
    "stop")
        echo "🛑 Stopping development container..."
        docker rm -f rag-dev-container
        echo "✅ Container stopped"
        ;;
    "status")
        echo "📊 Container status:"
        docker ps | grep rag-dev-container || echo "Container not running"
        echo ""
        echo "🏥 Health check:"
        curl -s http://localhost:5001/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker rm -f rag-dev-container 2>/dev/null || true
        docker rmi rag-agent-factory 2>/dev/null || true
        echo "✅ Cleanup complete"
        ;;
    "help")
        echo "📖 Available commands:"
        echo "  ./dev.sh build   - Build Docker image"
        echo "  ./dev.sh run     - Run container (requires build first)"
        echo "  ./dev.sh deploy  - Build and run (one command)"
        echo "  ./dev.sh logs    - View container logs"
        echo "  ./dev.sh stop    - Stop container"
        echo "  ./dev.sh status  - Check container and health status"
        echo "  ./dev.sh clean   - Remove container and image"
        echo "  ./dev.sh help    - Show this help"
        ;;
    *)
        echo "❓ Unknown command: $1"
        echo "📖 Run './dev.sh help' for available commands"
        exit 1
        ;;
esac
EOF

# Make dev script executable
chmod +x dev.sh

# Create README.md
echo "📖 Creating README.md..."
cat > README.md << 'EOF'
# RAG Agent Factory - Phase 1

A simple, modular Flask application that provides a Q&A interface with local Ollama models.

## Quick Start

### Prerequisites
- Docker installed and running
- Ollama service running (localhost:11434)
- Ollama model downloaded (e.g., `ollama pull llama3.2:3b`)

### Development Workflow

```bash
# Quick deployment (build + run)
./dev.sh deploy

# Individual steps
./dev.sh build    # Build Docker image
./dev.sh run      # Run container
./dev.sh logs     # View logs
./dev.sh stop     # Stop container
./dev.sh clean    # Remove everything

# Check status
./dev.sh status
```

### Manual Docker Commands

```bash
# Build image
docker build -t rag-agent-factory .

# Run container
docker run -d -p 5001:5000 --name rag-dev-container rag-agent-factory

# View logs
docker logs -f rag-dev-container
```

## Architecture

```
rag-agent-factory/
├── app.py                    # Main Flask application
├── config/settings.py        # Configuration management
├── llm/ollama_client.py      # Ollama integration
├── utils/error_handlers.py   # Error handling utilities
├── templates/                # HTML templates (Metropolis font)
├── static/                   # CSS and JavaScript
└── dev.sh                   # Development workflow script
```

## Features

- ✅ Simple question → answer interface
- ✅ Local Ollama integration (FERPA compliant)
- ✅ Clean, modular code structure
- ✅ Responsive web interface with Metropolis font
- ✅ Docker containerization
- ✅ Health monitoring
- ✅ Error handling and logging

## Phase 1 Goals

- [x] Basic Ollama integration
- [x] Docker deployment
- [x] Clean web interface
- [x] Modular code structure
- [ ] External domain deployment

## Next Steps (Phase 2)

- Document processing pipeline development
- Multi-format file support (PDF, images, etc.)
- RAG capabilities with vector storage
- Conversation memory

## Configuration

Environment variables can be set for customization:

- `OLLAMA_HOST`: Ollama service host (default: localhost)
- `OLLAMA_PORT`: Ollama service port (default: 11434)
- `OLLAMA_MODEL`: Model to use (default: llama3.2:3b)
- `FLASK_DEBUG`: Enable debug mode (default: False)

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull a model if none available
ollama pull llama3.2:3b
```

### Docker Issues
```bash
# Check Docker status
docker info

# View container logs
./dev.sh logs

# Restart everything
./dev.sh clean
./dev.sh deploy
```

### Port Conflicts
```bash
# Use different port
docker run -d -p 5002:5000 --name rag-dev-container rag-agent-factory
```

## Development Principles

This project follows these core principles:

1. **Simplicity over complexity** - Prefer readable, verbose code over clever solutions
2. **Modular design** - Easy component swapping and upgrades  
3. **Educational value** - Code should be self-documenting and learning-focused
4. **Iterative development** - Build incrementally with testing at each step

## License

Open source - built for educational and development purposes.
EOF

# Create empty log files
touch logs/.gitkeep
touch uploads/.gitkeep
touch temp/.gitkeep

# Final status
echo ""
echo "🎉 RAG Agent Factory - Phase 1 Setup Complete!"
echo "=============================================="
echo ""
echo "📁 Project created in: $(pwd)"
echo ""
echo "🚀 Next steps:"
echo "   1. cd rag-agent-factory"
echo "   2. ./dev.sh deploy"
echo "   3. Open http://localhost:5001"
echo ""
echo "🔧 Development commands:"
echo "   ./dev.sh help      # View all commands"
echo "   ./dev.sh deploy    # Quick build + run"
echo "   ./dev.sh logs      # View logs"
echo "   ./dev.sh status    # Check health"
echo ""
echo "📋 Prerequisites checklist:"
echo "   □ Docker running: docker info"
echo "   □ Ollama running: curl http://localhost:11434/api/tags"
echo "   □ Model available: ollama pull llama3.2:3b"
echo ""
echo "✅ Setup complete! Happy coding! 🎯"
