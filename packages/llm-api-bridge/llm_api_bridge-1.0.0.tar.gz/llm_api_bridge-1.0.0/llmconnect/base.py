"""
Base class for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional

class BaseLLM(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.7, max_tokens: int = 1024):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to the LLM and return the response
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The LLM's response as a clean text string
        """
        pass