"""
OpenAI LLM provider implementation
"""

import requests
import json
from typing import Dict, Any
from ..base import BaseLLM

class OpenAILLM(BaseLLM):
    """OpenAI LLM provider using REST API"""
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to OpenAI API
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The response from OpenAI
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
            raise Exception(f"OpenAI API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse OpenAI response: {str(e)}")