"""Supported third-party frameworks for LLMTrackingProxy.

Frameworks are optional integrations that enable special features for specific
libraries like LangChain. Most users should omit the framework parameter
(defaults to None) for direct API usage.

Framework vs Provider:
- Provider (REQUIRED): The actual LLM service (OpenAI, Anthropic, etc.)
- Framework (OPTIONAL): Integration layer for libraries like LangChain

Example usage:
    # Direct API usage (95% of cases) - framework=None by default
    LLMTrackingProxy(client, provider=Provider.OPENAI)

    # LangChain integration (5% of cases) - framework explicitly set
    LLMTrackingProxy(client, provider=Provider.OPENAI, framework=Framework.LANGCHAIN)
"""

from enum import Enum


class Framework(Enum):
    """Enum of supported frameworks.

    These are optional integration layers that enable special features
    for specific libraries. Most users don't need to set a framework.
    """

    LANGCHAIN = "langchain"  # Enables LangChain-specific optimizations
