# DeepSentinel Python SDK

The official Python SDK for DeepSentinel - AI compliance middleware for safe LLM interactions.

## Installation

```bash
pip install deepsentinel-sdk
```

## Quick Start

```python
from deepsentinel import SentinelClient

# Initialize the client
client = SentinelClient(
    sentinel_api_key="YOUR_DEEPSENTINEL_API_KEY",
    openai_api_key="YOUR_OPENAI_API_KEY"
)

# Send a compliant request
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello, world!"}]
)

print(response.choices[0].message.content)
```

## Features

- **🛡️ Compliance Checking**: Automatic detection of PII, PHI, and regulatory violations
- **🔄 Multiple Providers**: Support for OpenAI, Anthropic, and other LLM providers
- **📊 Audit Logging**: Comprehensive activity logging for compliance
- **⚡ Performance**: Local detection with smart caching
- **🔌 MCP Support**: Integration with Model Context Protocol
- **🌐 Streaming**: Full support for streaming responses

## Documentation

- [Developer Guide](../docs/developer-guide.md)
- [API Reference](https://deepsentinel-ai.github.io/deepsentinel-python)
- [Examples](../examples/python/)

## Requirements

- Python 3.8+
- API key from DeepSentinel
- API keys from supported LLM providers

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/deepsentinel/deepsentinel-sdk
cd deepsentinel-sdk/python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
isort .
flake8 .
mypy .
```

## License

MIT License - see [LICENSE](../LICENSE) for details.