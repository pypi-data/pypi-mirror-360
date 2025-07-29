# llmconnect/__init__.py
"""
LLMConnect - A unified interface for querying multiple LLM providers via REST APIs
"""

from .llmconnect import LLMConnect
from .base import BaseLLM

__version__ = "1.0.0"
__author__ = "LLMConnect Team"
__all__ = ["LLMConnect", "BaseLLM"]