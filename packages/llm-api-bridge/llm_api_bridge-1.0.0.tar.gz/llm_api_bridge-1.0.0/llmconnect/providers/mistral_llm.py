# llmconnect/providers/mistral_llm.py
"""
Mistral LLM provider implementation
"""

import requests
import json
from typing import Dict, Any
from ..base import BaseLLM

class MistralLLM(BaseLLM):
    """Mistral LLM provider using REST API"""
    
    BASE_URL = "https://api.mistral.ai/v1/chat/completions"
    
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to Mistral API
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The response from Mistral
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Mistral API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse Mistral response: {str(e)}")
