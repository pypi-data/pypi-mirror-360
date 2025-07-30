# LLMCosts

[![PyPI version](https://img.shields.io/pypi/v/llmcosts.svg)](https://pypi.org/project/llmcosts/)
[![Python Support](https://img.shields.io/pypi/pyversions/llmcosts.svg)](https://pypi.org/project/llmcosts/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LLMCosts** is a comprehensive LLM cost tracking and management platform that helps developers and agencies monitor, analyze, and optimize their AI spending across all major providers. **[Sign up for a free account at llmcosts.com](https://llmcosts.com)** to access real-time analytics, budget alerts, client billing tools, and accounting integrations.

A universal Python wrapper that intercepts LLM API responses and extracts usage information for comprehensive cost tracking. Works as a drop-in replacement for your existing LLM clients with zero code changes to your API calls.

**🔒 Privacy-First**: LLMCosts NEVER sees your API keys, requests, or responses. We only extract usage data (tokens, costs, model info) from responses. Unlike other frameworks that capture everything, we prioritize your privacy and security above all else.

**🔄 Universal Compatibility**: One tracking proxy works with ANY LLM provider's SDK. No need for different wrappers per provider - the same `LLMTrackingProxy` works with OpenAI, Anthropic, Google, AWS Bedrock, and any other provider.

**🎯 Supports**: OpenAI (any OpenAI-compatible APIs -- DeepSeek, Grok, etc.), Anthropic, Google Gemini, AWS Bedrock, and LangChain.

## 🚀 Quick Start

But wait! Just a quick note: 

> **🔑 CRITICAL: API Key Required**
>
> Before using LLMCosts, you **MUST** have an LLMCosts API key. **[Sign up for a free account at llmcosts.com](https://llmcosts.com)** to get your API key.
>
> **Without an API key, none of the LLMCosts tracking will work!**

### Installation

```bash
# Core library only (minimal dependencies)
pip install llmcosts

# To install llmcosts along with the SDKs from specific 
# providers (quote for zsh compatibility)  (for testing, etc)
pip install "llmcosts[openai]"      # OpenAI + compatible APIs (DeepSeek, Grok, etc.)
pip install "llmcosts[anthropic]"   # Anthropic Claude
pip install "llmcosts[google]"      # Google Gemini
pip install "llmcosts[bedrock]"     # AWS Bedrock
pip install "llmcosts[langchain]"   # LangChain integration

# All providers at once
pip install "llmcosts[all]"

# Using uv (recommended) - no quotes needed
uv add llmcosts                   # Core only
uv add llmcosts[openai]           # With OpenAI
uv add llmcosts[langchain]        # With LangChain
uv add llmcosts[all]              # All providers
```

### Basic Usage

```python
import os
from llmcosts import LLMTrackingProxy, Provider
import openai

# Create OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Wrap with LLMCosts tracking
tracked_client = LLMTrackingProxy(
    client, 
    provider=Provider.OPENAI,  # REQUIRED: Specifies the LLM service
    api_key=os.environ.get("LLMCOSTS_API_KEY"),  # Your LLMCosts API key
    debug=True
)

# Use exactly as before - zero changes to your API calls
response = tracked_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Usage automatically logged as structured JSON
# 🔒 Privacy: Only usage metadata is extracted - never your API keys, requests, or responses
```

### Environment Setup

LLMCosts only needs its own API key to function. You can pass it in as a parameter or LLMTrackingProxy can get it from an environment variable.

```bash
# Set your LLMCosts API key (get this from llmcosts.com)
export LLMCOSTS_API_KEY="your-llmcosts-api-key-here"
```

**🔒 Important**: Your existing LLM provider API keys (OpenAI, Anthropic, etc.) remain yours and are never shared with LLMCosts. You continue to use them exactly as before - LLMCosts only extracts usage metadata from responses.

> **💡 Recommended Pattern**: Always create `LLMTrackingProxy` directly - it handles global tracker creation, API key management, and background processing automatically.

## 📋 Key Features

- **🔄 Universal Compatibility**: One proxy works with ANY LLM provider's SDK - OpenAI, Anthropic, Google, AWS, and more
- **🔒 Privacy-First Design**: NEVER sees API keys, requests, or responses - only usage data (tokens, costs, model info)
- **🏢 Client-Level Tracking**: Seamlessly track costs per customer, user, project, or department with rich context data
- **📊 Automatic Usage Tracking**: Captures tokens, costs, model info, and timestamps from response metadata
- **🏷️ Rich Context Data**: Add any metadata - project names, user IDs, billing info, session data, or custom tags
- **💰 Multi-Tenant Ready**: Perfect for agencies, SaaS platforms, and enterprise cost allocation
- **🎛️ Dynamic Configuration**: Change settings on-the-fly without restarting
- **💾 Smart Delivery**: Resilient background delivery with retry logic
- **🔔 Response Callbacks**: Built-in SQLite/text file callbacks plus custom handlers
- **🔍 Debug Mode**: Synchronous operation for testing and debugging
- **📤 Structured Output**: Clean JSON format for easy parsing
- **♻️ Auto-Recovery**: Automatically restarts failed delivery threads
- **🚫 Non-Intrusive**: Original API responses remain completely unchanged

## 🎯 Supported Providers

| Provider | Provider Enum | Framework | Installation |
|----------|---------------|-----------|-------------|
| **OpenAI** | `Provider.OPENAI` | `None` (default) | `pip install "llmcosts[openai]"` |
| **Anthropic** | `Provider.ANTHROPIC` | `None` (default) | `pip install "llmcosts[anthropic]"` |
| **Google Gemini** | `Provider.GOOGLE` | `None` (default) | `pip install "llmcosts[google]"` |
| **AWS Bedrock** | `Provider.AMAZON_BEDROCK` | `None` (default) | `pip install "llmcosts[bedrock]"` |
| **DeepSeek** | `Provider.DEEPSEEK` | `None` (default) | `pip install "llmcosts[openai]"` |
| **Grok/xAI** | `Provider.XAI` | `None` (default) | `pip install "llmcosts[openai]"` |
| **LangChain + OpenAI** | `Provider.OPENAI` | `Framework.LANGCHAIN` | `pip install "llmcosts[langchain]"` |

## 📖 Documentation

### Core Guides

- **[🏢 Client Tracking & Context Data](docs/client-tracking.md)** - **⭐ ESSENTIAL** - Track costs per client, user, project with rich context data
- **[🔧 Configuration](docs/configuration.md)** - All configuration options, environment variables, and advanced settings
- **[🎯 Providers](docs/providers.md)** - Provider-specific integration guides with examples
- **[🔗 LangChain Integration](docs/langchain.md)** - Complete LangChain integration guide
- **[💰 Pricing & Models](docs/pricing.md)** - Model discovery, pricing info, and cost calculation
- **[🛠️ SDK Helper Functions](docs/sdk-functions.md)** - Complete reference for all SDK helper functions
- **[🔍 Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[🧪 Testing](docs/testing.md)** - Comprehensive testing documentation
- **[🚀 Deployment](docs/deployment.md)** - Deployment guide for PyPI and version management

### Quick Links

- **Getting Started**: See [Basic Usage](#basic-usage) above
- **🏢 Multi-Tenant Apps**: [Client Tracking Guide](docs/client-tracking.md) - Perfect for agencies & SaaS
- **Provider Setup**: [Providers Guide](docs/providers.md)
- **LangChain Users**: [LangChain Integration](docs/langchain.md)
- **Advanced Config**: [Configuration Guide](docs/configuration.md)
- **Having Issues?**: [Troubleshooting Guide](docs/troubleshooting.md)

## 💻 Quick Examples

### OpenAI

```python
from llmcosts import LLMTrackingProxy, Provider
import openai

client = openai.OpenAI(api_key="your-key")
tracked_client = LLMTrackingProxy(client, provider=Provider.OPENAI)

response = tracked_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Anthropic

```python
from llmcosts import LLMTrackingProxy, Provider
import anthropic

client = anthropic.Anthropic(api_key="your-key")
tracked_client = LLMTrackingProxy(client, provider=Provider.ANTHROPIC)

response = tracked_client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### LangChain

```python
from llmcosts import LLMTrackingProxy, Provider, Framework
from langchain_openai import ChatOpenAI
import openai

# Key difference: specify framework=Framework.LANGCHAIN
openai_client = openai.OpenAI(api_key="your-key")
tracked_client = LLMTrackingProxy(
    openai_client,
    provider=Provider.OPENAI,
    framework=Framework.LANGCHAIN  # Enable LangChain integration
)

chat_model = ChatOpenAI(client=tracked_client.chat.completions)
response = chat_model.invoke([{"role": "user", "content": "Hello!"}])
```

### Client Tracking (Multi-Tenant)

```python
from llmcosts import LLMTrackingProxy, Provider
import openai

client = openai.OpenAI(api_key="your-key")
tracked_client = LLMTrackingProxy(
    client,
    provider=Provider.OPENAI,
    client_customer_key="customer_acme_corp",  # Track costs per customer
    context={
        "user_id": "user_123",
        "project": "chatbot_v2", 
        "department": "support",
        "environment": "production"
    }
)

response = tracked_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
# → Automatically tracked with customer and context data for billing/analytics
```

> **See [Provider Integration Guide](docs/providers.md) for complete examples of all supported providers.**

## 🔍 Model Discovery & Pricing

```python
from llmcosts import list_models, get_model_pricing, calculate_cost_from_tokens, Provider

# Discover available models
models = list_models()
print(f"Total models: {len(models)}")

# Get pricing information
pricing = get_model_pricing(Provider.OPENAI, "gpt-4o-mini")
print(f"Input: ${pricing['costs'][0]['cost_per_million']}/M tokens")

# Calculate costs
cost = calculate_cost_from_tokens(
    Provider.OPENAI, "gpt-4o-mini", 
    input_tokens=1000, output_tokens=500
)
print(f"Total cost: ${cost['costs']['total_cost']}")
```

> **See [Pricing & Models Guide](docs/pricing.md) for complete model discovery and cost calculation features.**

## 🛠️ Development

### Setup

```bash
# Clone repository
git clone https://github.com/llmcosts/llmcosts-python.git
cd llmcosts-python

# Using uv (recommended)
uv sync --extra dev

# Using pip
pip install -e ".[dev]"
```

### Testing

```bash
# Quick test (requires your own OpenAI API key)
uv run python tests/check.py openai gpt-4o-mini

# Full test suite
uv run pytest

# With coverage
uv run pytest --cov=llmcosts --cov-report=html
```

**🔒 Testing Privacy**: Tests use YOUR provider API keys locally to verify functionality. These keys never leave your machine - they're only used for local testing.

> **See [Testing Guide](docs/testing.md) for comprehensive testing documentation including how to set up provider API keys for local testing.**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run the test suite: `uv run pytest`
5. Ensure code quality: `uv run black llmcosts/ tests/` and `uv run isort llmcosts/ tests/`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **🌐 Website**: [llmcosts.com](https://llmcosts.com)
- **📦 PyPI**: [pypi.org/project/llmcosts](https://pypi.org/project/llmcosts/)
- **🐙 GitHub**: [github.com/llmcosts/llmcosts-python](https://github.com/llmcosts/llmcosts-python)
- **🐛 Issues**: [github.com/llmcosts/llmcosts-python/issues](https://github.com/llmcosts/llmcosts-python/issues)
- **📧 Support**: [help@llmcosts.com](mailto:help@llmcosts.com)

## 📈 Changelog

### v0.2.2 (Current)
- New SDK helper functions with comprehensive documentation
- Enhanced events management with filtering, search, and export
- Added `list_threshold_events()` function for threshold event tracking
- Improved network resilience in tests with retry logic
- **Breaking changes**: Removed `limits.py`, `customers.py`, and `alerts.py` modules
- Migration guide available in [CHANGELOG.md](CHANGELOG.md)

### v0.1.0
- Universal LLM provider support
- Dynamic configuration with property setters
- Context tracking for user/session data
- Response callbacks for custom processing
- Synchronous mode for testing
- Resilient background delivery
- Comprehensive test coverage
- Thread-safe global tracker management
