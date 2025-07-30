"""
Provider enum for LLM tracking.

Providers represent the actual LLM services (OpenAI, Anthropic, etc.) and are
REQUIRED for all LLMTrackingProxy usage. This is different from frameworks,
which are optional integration layers.

Provider vs Framework:
- Provider (REQUIRED): The actual LLM service providing the models
- Framework (OPTIONAL): Integration layer like LangChain (usually None)

Example:
    # Provider is always required
    LLMTrackingProxy(client, provider=Provider.OPENAI)

    # Framework is only needed for special integrations
    LLMTrackingProxy(client, provider=Provider.OPENAI, framework=Framework.LANGCHAIN)
"""

from enum import Enum


class Provider(Enum):
    """Enum of supported LLM providers.

    These represent the actual LLM services and are required for all tracking.
    Choose the provider that matches your LLM service, regardless of how you
    access it (direct API, LangChain, etc.).
    """

    AMAZON_BEDROCK = "amazon-bedrock"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    DEEPSEEK = "deepseek"
    GITHUB_COPILOT = "github-copilot"
    GOOGLE = "google"
    GROQ = "groq"
    LLAMA = "llama"
    MISTRAL = "mistral"
    MORPH = "morph"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    VERCEL = "vercel"
    VERTEX = "vertex"
    XAI = "xai"
