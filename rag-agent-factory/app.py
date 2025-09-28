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
ollama_client = OllamaClient(
    host=app.config.get('OLLAMA_HOST', 'localhost'),
    port=app.config.get('OLLAMA_PORT', '11434'),
    model=app.config.get('OLLAMA_MODEL', 'llama3.2:3b')
)

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
