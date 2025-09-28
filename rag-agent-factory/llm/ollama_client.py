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
    			"stream": False,
    			"options": {
        			"temperature": 0.6,
        			"top_p": 0.9,
        			"num_predict": 2048
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
