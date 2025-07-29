<<<<<<< HEAD
# DeepSentinel SDK

A developer-friendly SDK that provides a middleware layer between applications and LLM providers, with comprehensive compliance checks, audit logging, and performance optimizations for AI safety and compliance.

## 🚀 Quick Start

### Python
=======
# DeepSentinel Python SDK

The official Python SDK for DeepSentinel - AI compliance middleware for safe LLM interactions.

## Installation
>>>>>>> dbee941d4b0fac0531f46a9d02f258d5f36c3687

```bash
pip install deepsentinel-sdk
```

<<<<<<< HEAD
=======
## Quick Start

>>>>>>> dbee941d4b0fac0531f46a9d02f258d5f36c3687
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

<<<<<<< HEAD
### TypeScript

```bash
npm install @deepsentinel/sdk
```

```typescript
import { SentinelClient } from '@deepsentinel/sdk';

const client = new SentinelClient({
  sentinelApiKey: 'YOUR_DEEPSENTINEL_API_KEY',
  providers: {
    openai: { apiKey: 'YOUR_OPENAI_API_KEY' }
  }
});

const response = await client.chat.completions.create({
  model: 'gpt-4o',
  messages: [{role: 'user', content: 'Hello, world!'}]
});

console.log(response.choices[0].message.content);
```

## ✨ Features
=======
## Features
>>>>>>> dbee941d4b0fac0531f46a9d02f258d5f36c3687

- **🛡️ Compliance Checking**: Automatic detection of PII, PHI, and regulatory violations
- **🔄 Multiple Providers**: Support for OpenAI, Anthropic, and other LLM providers
- **📊 Audit Logging**: Comprehensive activity logging for compliance
- **⚡ Performance**: Local detection with smart caching
- **🔌 MCP Support**: Integration with Model Context Protocol
- **🌐 Streaming**: Full support for streaming responses

<<<<<<< HEAD
## 📚 Documentation

- **[Getting Started](docs/developer-guide.md)** - Installation and basic usage
- **[Architecture Guide](docs/architecture-guide.md)** - System design and components
- **[Development Guidelines](docs/development-guidelines.md)** - Contributing and best practices
- **[API Reference](https://docs.deepsentinel.ai)** - Complete API documentation

## 🏗️ Repository Structure

This is a monorepo containing:

- [`python/`](python/) - Python SDK implementation
- [`typescript/`](typescript/) - TypeScript/JavaScript SDK implementation
- [`examples/`](examples/) - Usage examples for all languages
- [`docs/`](docs/) - Comprehensive documentation
- [`shared/`](shared/) - Shared resources and schemas

## 🚦 Project Status

- ✅ **Planning Phase**: Complete architecture and documentation
- 🔄 **Phase 1**: Python SDK development (in progress)
- ⏳ **Phase 2**: TypeScript SDK development (planned)
- ⏳ **Phase 3**: Advanced features and MCP integration (planned)

## 🤝 Contributing

We welcome contributions! Please see our [Development Guidelines](docs/development-guidelines.md) for details on:

- Code style and best practices
- Testing requirements
- Pull request process
- Documentation standards

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://docs.deepsentinel.ai](https://docs.deepsentinel.ai)
- **Examples**: [examples/](examples/)
- **Issues**: [GitHub Issues](https://github.com/deepsentinel/deepsentinel-sdk/issues)
- **Support**: [support@deepsentinel.ai](mailto:support@deepsentinel.ai)

---

Made with ❤️ by the DeepSentinel team
=======
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
>>>>>>> dbee941d4b0fac0531f46a9d02f258d5f36c3687
