# test_llmconnect.py
"""
Example usage and test file for LLMConnect
"""

from llmconnect import LLMConnect

def test_llmconnect():
    """Test LLMConnect with different providers"""
    
    # Test OpenAI
    try:
        openai_client = LLMConnect("gpt-4", "your-openai-api-key")
        response = openai_client.chat("Hello, how are you?")
        print(f"OpenAI Response: {response}")
    except Exception as e:
        print(f"OpenAI Error: {e}")
    
    # Test Claude
    try:
        claude_client = LLMConnect("claude-3-sonnet", "your-claude-api-key")
        response = claude_client.chat("What's the weather like?")
        print(f"Claude Response: {response}")
    except Exception as e:
        print(f"Claude Error: {e}")
    
    # Test Gemini
    try:
        gemini_client = LLMConnect("gemini-pro", "your-gemini-api-key")
        response = gemini_client.chat("Tell me a joke")
        print(f"Gemini Response: {response}")
    except Exception as e:
        print(f"Gemini Error: {e}")
    
    # Test with custom parameters
    try:
        custom_client = LLMConnect(
            model_name="gpt-4", 
            api_key="your-api-key",
            temperature=0.9,
            max_tokens=2048
        )
        response = custom_client.chat("Write a short story")
        print(f"Custom Response: {response}")
    except Exception as e:
        print(f"Custom Error: {e}")

if __name__ == "__main__":
    test_llmconnect()