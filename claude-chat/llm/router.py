"""
LLM Router - Manages routing between Local Models and Claude
Phase 1: Simple manual routing (no auto-switching)
Supports: General, Coder, and Claude models
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class ModelRouter:
    """
    Routes queries between local LLMs and Claude
    Now supports three models: General, Coder, and Claude
    """
    
    # Model identifiers
    LOCAL_GENERAL = "local-general"
    LOCAL_CODER = "local-coder"
    CLAUDE_MODEL = "claude"
    
    def __init__(self):
        """Initialize router"""
        self.last_model_used = self.LOCAL_GENERAL
        logger.info("ModelRouter initialized with 3 models (General, Coder, Claude)")
    
    def route_query(
        self, 
        user_preference: str,
        query: str = None
    ) -> Tuple[str, str, bool]:
        """
        Determine which model should handle the query
        
        Phase 1: Simply honors user preference
        Phase 2: Will analyze query and potentially override
        
        Args:
            user_preference: "local-general", "local-coder", or "claude"
            query: The user's question (unused in Phase 1)
        
        Returns:
            tuple: (
                model_to_use: str,      # Which model to use
                reason: str,            # Why this model was chosen
                auto_switched: bool     # True if system overrode user choice
            )
        """
        # Phase 1: Always honor user preference
        model_to_use = user_preference
        reason = "User selected"
        auto_switched = False
        
        # Track for stats
        self.last_model_used = model_to_use
        
        logger.info(f"Routing to {model_to_use}: {reason}")
        
        return model_to_use, reason, auto_switched
    
    def get_model_name_for_ollama(self, model_id: str) -> str:
        """
        Convert model ID to actual Ollama model name
        
        Args:
            model_id: Internal model identifier
        
        Returns:
            str: Ollama model name to use
        """
        model_map = {
            self.LOCAL_GENERAL: "qwen2.5:14b",
            self.LOCAL_CODER: "qwen2.5-coder:14b",
        }
        
        return model_map.get(model_id, "qwen2.5:14b")
    
    def get_model_display_name(self, model_id: str) -> str:
        """
        Get human-readable model name for UI
        
        Args:
            model_id: Model identifier or Ollama model name
        
        Returns:
            str: Display name for UI
        """
        display_names = {
            # Internal IDs
            self.LOCAL_GENERAL: "Local (Qwen2.5 14B)",
            self.LOCAL_CODER: "Local Coder (Qwen2.5 14B)",
            self.CLAUDE_MODEL: "Claude Sonnet 4.5",
            
            # Ollama model names
            "qwen2.5:14b": "Local (Qwen2.5 14B)",
            "qwen2.5-coder:14b": "Local Coder (Qwen2.5 14B)",
            
            # Claude model names
            "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
        }
        
        return display_names.get(model_id, model_id)
    
    def get_model_icon(self, model_id: str) -> str:
        """
        Get emoji icon for model
        
        Args:
            model_id: Model identifier
        
        Returns:
            str: Emoji icon
        """
        icons = {
            self.LOCAL_GENERAL: "🖥️",
            self.LOCAL_CODER: "💻",
            self.CLAUDE_MODEL: "⚡",
        }
        
        return icons.get(model_id, "🤖")


# Phase 2 Preview: Auto-routing logic (commented out for now)
"""
class IntelligentRouter(ModelRouter):
    '''
    Smart router that automatically selects best model based on query
    '''
    
    # Complexity indicators
    COMPLEX_KEYWORDS = [
        'analyze', 'detailed', 'comprehensive', 'research',
        'compare', 'evaluate', 'explain in depth', 'write a report',
    ]
    
    # Code indicators
    CODE_KEYWORDS = [
        'function', 'class', 'def ', 'import', 'algorithm',
        'bug', 'debug', 'refactor', 'implement', 'code',
        '```', 'python', 'javascript', 'java', 'c++',
    ]
    
    def analyze_query_type(self, query: str) -> Tuple[str, str]:
        '''
        Determine which model is best for this query
        Returns: (model_id: str, reason: str)
        '''
        query_lower = query.lower()
        
        # 1. Check for code-related queries
        if any(kw in query_lower for kw in self.CODE_KEYWORDS):
            return self.LOCAL_CODER, "Code-related query"
        
        # 2. Check for complex tasks needing Claude
        if len(query) > 500:
            return self.CLAUDE_MODEL, "Long complex query"
        
        if any(kw in query_lower for kw in self.COMPLEX_KEYWORDS):
            return self.CLAUDE_MODEL, "Complex analysis required"
        
        # 3. Default to general model for everything else
        return self.LOCAL_GENERAL, "General query"
    
    def route_query(self, user_preference: str, query: str = None):
        '''Route with intelligence'''
        
        # If query provided, analyze it
        if query:
            best_model, reason = self.analyze_query_type(query)
            
            # Auto-switch if different from user preference
            if best_model != user_preference:
                logger.info(f"Auto-switching from {user_preference} to {best_model}: {reason}")
                return best_model, reason, True  # auto_switched=True
        
        # Otherwise honor user preference
        return user_preference, "User selected", False
"""