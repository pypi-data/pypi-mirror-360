# llmconnect/providers/claude_llm.py
"""
Claude (Anthropic) LLM provider implementation
"""

import requests
import json
from typing import Dict, Any
from ..base import BaseLLM

class ClaudeLLM(BaseLLM):
    """Claude LLM provider using REST API"""
    
    BASE_URL = "https://api.anthropic.com/v1/messages"
    
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to Claude API
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The response from Claude
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
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
            return data["content"][0]["text"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse Claude response: {str(e)}")
