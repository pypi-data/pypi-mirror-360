"""
Dedicated tests for LangChain limits and thresholds integration.

Focus: LangChain API calls with limits and thresholds applied.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import openai
import pytest
from environs import Env

# Add the parent directory to sys.path so we can import from the main project
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmcosts.exceptions import TriggeredLimitError
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider
from llmcosts.tracker.frameworks import Framework

# Load environment variables from .env file in the tests directory
env = Env()
env.read_env(Path(__file__).parent / ".env")


@pytest.fixture
def openai_client():
    """Create a real OpenAI client for LangChain to use."""
    api_key = env.str("OPENAI_API_KEY", None)
    if not api_key:
        pytest.skip(
            "OPENAI_API_KEY not found in environment variables or tests/.env file"
        )
    return openai.OpenAI(api_key=api_key)


@pytest.fixture
def tracked_client(openai_client):
    """Create a tracked OpenAI client for LangChain."""
    tracked_client = LLMTrackingProxy(
        openai_client,
        provider=Provider.OPENAI,
        debug=True,
        framework=Framework.LANGCHAIN,
    )
    return tracked_client


@pytest.fixture
def langchain_llm(tracked_client):
    """Create a LangChain OpenAI LLM using the tracked client."""
    try:
        from langchain_openai import OpenAI
    except ImportError:
        pytest.skip("langchain-openai not installed")

    return OpenAI(
        client=tracked_client.completions,
        model="gpt-3.5-turbo-instruct",
        max_tokens=20,
        temperature=0.1,
    )


@pytest.fixture
def langchain_chat_model(tracked_client):
    """Create a LangChain ChatOpenAI model using the tracked client."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        pytest.skip("langchain-openai not installed")

    return ChatOpenAI(
        client=tracked_client.chat.completions,
        model="gpt-4o-mini",
        max_tokens=20,
        temperature=0.1,
    )


def _allow():
    """Return a mock response indicating the request is allowed."""
    return {"status": "checked", "allowed": True, "violations": [], "warnings": []}


def _block():
    """Return a mock response indicating the request is blocked."""
    violation = {
        "event_id": "ca23a271-7419-48ab-871f-b9eb36a2c73d",
        "threshold_type": "limit",
        "amount": "1.00",
        "period": "daily",
        "triggered_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-01-02T00:00:00Z",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "client_customer_key": None,
        "message": "Usage blocked: limit threshold of $1.00 exceeded",
    }
    return {
        "status": "checked",
        "allowed": False,
        "violations": [violation],
        "warnings": [],
    }


class TestLangChainLimit:
    """Test suite for LangChain limits and thresholds."""

    # ========================================================================
    # LANGCHAIN COMPLETION LIMIT TESTS
    # ========================================================================

    def test_langchain_completion_nonstreaming_allowed(
        self, langchain_llm, tracked_client
    ):
        """Test LangChain completion (non-streaming) is allowed when thresholds pass."""
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            response = langchain_llm.invoke("Say hello")
            assert response
            assert len(response.strip()) > 0

    def test_langchain_completion_nonstreaming_blocked(
        self, langchain_llm, tracked_client
    ):
        """Test LangChain completion (non-streaming) is blocked when thresholds fail."""
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                langchain_llm.invoke("Say hello")

    def test_langchain_completion_streaming_allowed(self, tracked_client):
        """Test LangChain completion (streaming) is allowed when thresholds pass."""
        try:
            from langchain_openai import OpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        langchain_llm = OpenAI(
            client=tracked_client.completions,
            model="gpt-3.5-turbo-instruct",
            max_tokens=20,
            temperature=0.1,
            streaming=True,
        )

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            response_chunks = list(langchain_llm.stream("Count to 3"))
            assert len(response_chunks) > 0

    def test_langchain_completion_streaming_blocked(self, tracked_client):
        """Test LangChain completion (streaming) is blocked when thresholds fail."""
        try:
            from langchain_openai import OpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        langchain_llm = OpenAI(
            client=tracked_client.completions,
            model="gpt-3.5-turbo-instruct",
            max_tokens=20,
            temperature=0.1,
            streaming=True,
        )

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                list(langchain_llm.stream("Count to 3"))

    # ========================================================================
    # LANGCHAIN CHAT LIMIT TESTS
    # ========================================================================

    def test_langchain_chat_nonstreaming_allowed(
        self, langchain_chat_model, tracked_client
    ):
        """Test LangChain ChatOpenAI (non-streaming) is allowed when thresholds pass."""
        from langchain_core.messages import HumanMessage

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            messages = [HumanMessage(content="Say hello")]
            response = langchain_chat_model.invoke(messages)
            assert response
            assert hasattr(response, "content")
            assert len(response.content.strip()) > 0

    def test_langchain_chat_nonstreaming_blocked(
        self, langchain_chat_model, tracked_client
    ):
        """Test LangChain ChatOpenAI (non-streaming) is blocked when thresholds fail."""
        from langchain_core.messages import HumanMessage

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                messages = [HumanMessage(content="Say hello")]
                langchain_chat_model.invoke(messages)

    def test_langchain_chat_streaming_allowed(self, tracked_client):
        """Test LangChain ChatOpenAI (streaming) is allowed when thresholds pass."""
        try:
            from langchain_core.messages import HumanMessage
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        langchain_chat_model = ChatOpenAI(
            client=tracked_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=20,
            temperature=0.1,
            streaming=True,
        )

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            messages = [HumanMessage(content="Count to 3")]
            response_chunks = list(langchain_chat_model.stream(messages))
            assert len(response_chunks) > 0

    def test_langchain_chat_streaming_blocked(self, tracked_client):
        """Test LangChain ChatOpenAI (streaming) is blocked when thresholds fail."""
        try:
            from langchain_core.messages import HumanMessage
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        langchain_chat_model = ChatOpenAI(
            client=tracked_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=20,
            temperature=0.1,
            streaming=True,
        )

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                messages = [HumanMessage(content="Count to 3")]
                list(langchain_chat_model.stream(messages))

    # ========================================================================
    # LANGCHAIN CHAIN LIMIT TESTS
    # ========================================================================

    def test_langchain_chain_nonstreaming_allowed(
        self, langchain_chat_model, tracked_client
    ):
        """Test LangChain chain (non-streaming) is allowed when thresholds pass."""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([("human", "Say {word}")])

        chain = prompt | langchain_chat_model | StrOutputParser()

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            response = chain.invoke({"word": "hello"})
            assert response
            assert len(response.strip()) > 0

    def test_langchain_chain_nonstreaming_blocked(
        self, langchain_chat_model, tracked_client
    ):
        """Test LangChain chain (non-streaming) is blocked when thresholds fail."""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([("human", "Say {word}")])

        chain = prompt | langchain_chat_model | StrOutputParser()

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                chain.invoke({"word": "hello"})

    def test_langchain_chain_streaming_allowed(self, tracked_client):
        """Test LangChain chain (streaming) is allowed when thresholds pass."""
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        langchain_chat_model = ChatOpenAI(
            client=tracked_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=20,
            temperature=0.1,
            streaming=True,
        )

        prompt = ChatPromptTemplate.from_messages([("human", "Count to {number}")])

        chain = prompt | langchain_chat_model | StrOutputParser()

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            response_chunks = list(chain.stream({"number": "3"}))
            assert len(response_chunks) > 0

    def test_langchain_chain_streaming_blocked(self, tracked_client):
        """Test LangChain chain (streaming) is blocked when thresholds fail."""
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        langchain_chat_model = ChatOpenAI(
            client=tracked_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=20,
            temperature=0.1,
            streaming=True,
        )

        prompt = ChatPromptTemplate.from_messages([("human", "Count to {number}")])

        chain = prompt | langchain_chat_model | StrOutputParser()

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                list(chain.stream({"number": "3"}))

    # ========================================================================
    # BATCH OPERATION LIMIT TESTS
    # ========================================================================

    def test_langchain_batch_allowed(self, langchain_chat_model, tracked_client):
        """Test LangChain batch operations are allowed when thresholds pass."""
        from langchain_core.messages import HumanMessage

        message_batches = [
            [HumanMessage(content="Hi")],
            [HumanMessage(content="Hello")],
        ]

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            responses = langchain_chat_model.batch(message_batches)
            assert len(responses) == 2
            for response in responses:
                assert response
                assert hasattr(response, "content")
                assert len(response.content.strip()) > 0

    def test_langchain_batch_blocked(self, langchain_chat_model, tracked_client):
        """Test LangChain batch operations are blocked when thresholds fail."""
        from langchain_core.messages import HumanMessage

        message_batches = [
            [HumanMessage(content="Hi")],
            [HumanMessage(content="Hello")],
        ]

        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                langchain_chat_model.batch(message_batches)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
