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
