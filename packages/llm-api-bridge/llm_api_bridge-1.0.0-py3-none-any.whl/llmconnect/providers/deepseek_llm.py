# llmconnect/providers/deepseek_llm.py
"""
DeepSeek LLM provider implementation
"""

import requests
import json
from typing import Dict, Any
from ..base import BaseLLM

class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM provider using REST API"""
    
    BASE_URL = "https://api.deepseek.com/chat/completions"
    
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to DeepSeek API
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The response from DeepSeek
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse DeepSeek response: {str(e)}")
