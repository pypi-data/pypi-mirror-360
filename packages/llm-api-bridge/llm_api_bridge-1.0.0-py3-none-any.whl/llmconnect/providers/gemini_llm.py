# llmconnect/providers/gemini_llm.py
"""
Gemini LLM provider implementation
"""

import requests
import json
from typing import Dict, Any
from ..base import BaseLLM

class GeminiLLM(BaseLLM):
    """Gemini LLM provider using REST API"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def chat(self, prompt: str) -> str:
        """
        Send a chat message to Gemini API
        
        Args:
            prompt (str): The user's message/prompt
            
        Returns:
            str: The response from Gemini
        """
        headers = {
            "X-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}/{self.model_name}:generateContent"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse Gemini response: {str(e)}")
