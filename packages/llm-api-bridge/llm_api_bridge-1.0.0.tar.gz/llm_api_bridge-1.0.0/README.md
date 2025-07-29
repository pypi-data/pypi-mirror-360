# LLMConnect

A unified Python library for querying multiple Large Language Models (LLMs) using direct REST API calls.

## Features

- **Multi-Provider Support**: Connect to OpenAI, Claude, Gemini, Perplexity, Mistral, DeepSeek, and LLaMA
- **Auto-Detection**: Automatically detects the provider based on model name prefix
- **Simple Interface**: Just provide model name and API key
- **Customizable**: Optional temperature and max_tokens parameters
- **No SDKs Required**: Uses direct REST API calls via requests library

## Installation

```bash
pip install llmconnect
```

## Quick Start

```python
from llmconnect import LLMConnect

# Initialize with your preferred model
client = LLMConnect("gpt-4", "your-openai-api-key")

# Send a message
response = client.chat("Hello, how are you?")
print(response)
```

## Supported Models

- **OpenAI**: gpt-4, gpt-3.5-turbo, etc.
- **Claude**: claude-3-sonnet, claude-3-opus, etc.
- **Gemini**: gemini-pro, gemini-ultra, etc.
- **Perplexity**: sonar-pro, sonar-medium, etc.
- **Mistral**: mistral-large-latest, mistral-medium, etc.
- **DeepSeek**: deepseek-chat, deepseek-coder, etc.
- **LLaMA**: llama3-70b, llama2-13b, etc.

## Advanced Usage

```python
# Custom parameters
client = LLMConnect(
    model_name="claude-3-sonnet",
    api_key="your-claude-api-key",
    temperature=0.9,
    max_tokens=2048
)

response = client.chat("Write a creative story")
```

## API Keys

You'll need API keys from the respective providers:
- OpenAI: https://platform.openai.com/
- Anthropic (Claude): https://console.anthropic.com/
- Google (Gemini): https://makersuite.google.com/
- Perplexity: https://www.perplexity.ai/
- Mistral: https://console.mistral.ai/
- DeepSeek: https://platform.deepseek.com/
- LLaMA: https://www.llama-api.com/

## License

MIT License