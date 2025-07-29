# llmconnect/llmconnect.py
"""
Main router for LLMConnect that selects the appropriate provider
"""

from typing import Dict, Type, Optional
from .base import BaseLLM
from .providers.openai_llm import OpenAILLM
from .providers.claude_llm import ClaudeLLM
from .providers.gemini_llm import GeminiLLM
from .providers.perplexity_llm import PerplexityLLM
from .providers.mistral_llm import MistralLLM
from .providers.deepseek_llm import DeepSeekLLM
from .providers.llama_llm import LlamaLLM

class LLMConnect:
    """Main class for connecting to various LLM providers"""
    
    # Model name prefixes mapped to their provider classes
    PROVIDER_MAP: Dict[str, Type[BaseLLM]] = {
        'gpt': OpenAILLM,
        'claude': ClaudeLLM,
        'gemini': GeminiLLM,
        'sonar': PerplexityLLM,
        'mistral': MistralLLM,
        'deepseek': DeepSeekLLM,
        'llama': LlamaLLM,
    }
    
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.7, max_tokens: int = 1024):
        """
        Initialize LLMConnect with the specified model and parameters
        
        Args:
            model_name (str): Model name (e.g., "gpt-4.1", "claude-3-sonnet")
            api_key (str): API key for the provider
            temperature (float): Temperature for response generation (default: 0.7)
            max_tokens (int): Maximum tokens in response (default: 1024)
        """
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Auto-detect provider based on model name prefix
        self.provider = self._get_provider()
    
    def _get_provider(self) -> BaseLLM:
        """
        Auto-detect the provider based on model name prefix
        
        Returns:
            BaseLLM: Instance of the appropriate provider class
            
        Raises:
            ValueError: If no matching provider is found
        """
        model_lower = self.model_name.lower()
        
        for prefix, provider_class in self.PROVIDER_MAP.items():
            if model_lower.startswith(prefix):
                return provider_class(
                    model_name=self.model_name,
                    api_key=self.api_key,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
        
        raise ValueError(f"No provider found for model: {self.model_name}")
    
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to the LLM and return the response
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The LLM's response as a clean text string
        """
        return self.provider.chat(prompt)
