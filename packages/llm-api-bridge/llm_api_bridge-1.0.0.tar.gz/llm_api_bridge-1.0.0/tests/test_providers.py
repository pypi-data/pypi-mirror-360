# test_installation.py
"""
Quick test to verify LLMConnect installation and provider detection
"""

from llmconnect import LLMConnect

def test_installation():
    """Test that the package is properly installed"""
    print("🔍 Testing LLMConnect Installation...")
    
    # Test provider detection
    test_cases = [
        ("gpt-4", "OpenAILLM"),
        ("claude-3-sonnet", "ClaudeLLM"),
        ("gemini-2.0-flash", "GeminiLLM"),
        ("sonar-pro", "PerplexityLLM"),
        ("mistral-large-latest", "MistralLLM"),
        ("deepseek-chat", "DeepSeekLLM"),
        ("llama3-70b", "LlamaLLM")
    ]
    
    print("\n📋 Provider Detection Test:")
    print("-" * 50)
    
    for model_name, expected_class in test_cases:
        try:
            client = LLMConnect(model_name, "test-api-key")
            actual_class = client.provider.__class__.__name__
            
            if actual_class == expected_class:
                print(f"✅ {model_name:<20} -> {actual_class}")
            else:
                print(f"❌ {model_name:<20} -> Expected: {expected_class}, Got: {actual_class}")
                
        except Exception as e:
            print(f"❌ {model_name:<20} -> Error: {str(e)}")
    
    print("\n🔧 Parameter Test:")
    print("-" * 50)
    
    try:
        # Test custom parameters
        client = LLMConnect(
            model_name="gpt-4.1",
            api_key="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",
            temperature=0.9,
            max_tokens=2048
        )
        
        print(f"✅ Custom parameters: temp={client.temperature}, tokens={client.max_tokens}")
        
    except Exception as e:
        print(f"❌ Custom parameters failed: {e}")
    
    print("\n❌ Invalid Model Test:")
    print("-" * 50)
    
    try:
        # Test invalid model (should raise ValueError)
        client = LLMConnect("invalid-model-name", "test-key")
        print("❌ Should have raised ValueError for invalid model")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n🎉 Installation test completed!")

if __name__ == "__main__":
    test_installation()