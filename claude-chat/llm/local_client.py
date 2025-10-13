"""
Local LLM Client for Qwen2.5 14B via Ollama
Handles communication with locally-running Ollama instance
"""

import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LocalLLMClient:
    """
    Client for interacting with Ollama-hosted local LLM
    Designed for Qwen2.5 14B but works with any Ollama model
    """
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 11434,
        model: str = "qwen2.5:14b"
    ):
        """
        Initialize local LLM client
        
        Args:
            host: Ollama server host (default: localhost)
            port: Ollama server port (default: 11434)
            model: Model name in Ollama (default: qwen2.5:14b)
        """
        self.base_url = f"http://{host}:{port}"
        self.model = model
        logger.info(f"Initialized LocalLLMClient with model: {model}")
    
    def test_connection(self) -> bool:
        """
        Test if Ollama server is reachable and model is available
        
        Returns:
            bool: True if connected and model available
        """
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code != 200:
                logger.error(f"Ollama server returned status {response.status_code}")
                return False
            
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            if self.model not in model_names:
                logger.warning(f"Model {self.model} not found. Available: {model_names}")
                return False
            
            logger.info(f"Successfully connected to Ollama with model {self.model}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def get_response(
        self, 
        question: str, 
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Dict:
        """
        Get response from local LLM
        
        Args:
            question: User's question/prompt
            max_tokens: Maximum tokens to generate (default: 1024)
            temperature: Creativity level 0-1 (default: 0.7)
        
        Returns:
            dict: {
                'response': str,      # The actual response text
                'tokens': int,        # Number of tokens generated
                'duration_ms': int,   # Time taken in milliseconds
                'model': str          # Model name used
            }
        
        Raises:
            Exception: If request fails or Ollama returns error
        """
        try:
            logger.info(f"Sending query to {self.model}: {question[:50]}...")
            
            # Make request to Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": question,
                    "stream": False,  # Get complete response at once
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=60  # Allow up to 60 seconds for response
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama returned status {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Parse response
            data = response.json()
            
            result = {
                'response': data.get('response', ''),
                'tokens': data.get('eval_count', 0),
                'duration_ms': data.get('total_duration', 0) // 1_000_000,  # Convert ns to ms
                'model': self.model
            }
            
            logger.info(
                f"Response received: {result['tokens']} tokens in {result['duration_ms']}ms"
            )
            
            return result
            
        except requests.exceptions.Timeout:
            error_msg = "Local LLM request timed out (>60s)"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to reach Ollama server: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error in local LLM: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_model_info(self) -> Optional[Dict]:
        """
        Get information about the current model
        
        Returns:
            dict: Model details (size, family, parameters, etc.)
            None: If request fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None


# Convenience function for simple usage
def quick_query(question: str, model: str = "qwen2.5:14b") -> str:
    """
    Quick one-off query to local LLM
    
    Args:
        question: Question to ask
        model: Model name (default: qwen2.5:14b)
    
    Returns:
        str: Response text
    """
    client = LocalLLMClient(model=model)
    result = client.get_response(question)
    return result['response']