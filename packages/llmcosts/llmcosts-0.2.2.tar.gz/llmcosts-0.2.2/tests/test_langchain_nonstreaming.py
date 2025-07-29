"""
Dedicated tests for LangChain non-streaming usage tracking and cost event integration.

Focus: Non-streaming LangChain API calls using OpenAI LLM wrapper.
"""

import sys
from pathlib import Path

import openai
import pytest
from environs import Env

# Add the parent directory to sys.path so we can import from the main project
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.frameworks import Framework
from llmcosts.tracker.providers import Provider

# Load environment variables from .env file in the tests directory
env = Env()
env.read_env(Path(__file__).parent / ".env")


class TestLangChainNonStreaming:
    """Test suite for LLMTrackingProxy with LangChain non-streaming calls."""

    @pytest.fixture
    def openai_client(self):
        """Create a real OpenAI client for LangChain to use."""
        api_key = env.str("OPENAI_API_KEY", None)
        if not api_key:
            pytest.skip(
                "OPENAI_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )

        return openai.OpenAI(api_key=api_key)

    @pytest.fixture
    def tracked_openai_client(self, openai_client):
        """Create a tracked OpenAI client for LangChain."""
        tracked_client = LLMTrackingProxy(
            openai_client,
            provider=Provider.OPENAI,
            debug=True,
            framework=Framework.LANGCHAIN,
        )
        return tracked_client

    @pytest.fixture
    def langchain_llm(self, openai_client):
        """Create a LangChain OpenAI LLM using a tracked approach."""
        try:
            from langchain_openai import OpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Create LangChain LLM normally, we'll track it by wrapping the underlying client
        langchain_llm = OpenAI(
            model="gpt-3.5-turbo-instruct",  # LangChain's OpenAI wrapper typically uses instruct models
            max_tokens=50,
            temperature=0.1,
        )

        # Replace the internal client with our tracked client
        from llmcosts.tracker import LLMTrackingProxy

        langchain_llm.client = LLMTrackingProxy(
            langchain_llm.client,
            provider=Provider.OPENAI,
            framework=Framework.LANGCHAIN,
            debug=True,
        )

        return langchain_llm

    @pytest.fixture
    def langchain_chat_model(self, openai_client):
        """Create a LangChain ChatOpenAI model using a tracked approach."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Create LangChain ChatOpenAI normally, we'll track it by wrapping the underlying client
        langchain_chat_model = ChatOpenAI(
            model="gpt-4o-mini",
            max_tokens=50,
            temperature=0.1,
        )

        # Replace the internal client with our tracked client
        from llmcosts.tracker import LLMTrackingProxy

        langchain_chat_model.client = LLMTrackingProxy(
            langchain_chat_model.client,
            provider=Provider.OPENAI,
            framework=Framework.LANGCHAIN,
            debug=True,
        )

        return langchain_chat_model

    # ========================================================================
    # LANGCHAIN COMPLETION TESTS - NON-STREAMING
    # ========================================================================

    def test_langchain_completion_non_streaming(self, langchain_llm, caplog):
        """Test LangChain completion (non-streaming) captures usage."""
        prompt = "Tell me a short joke"

        # Make LangChain call
        response = langchain_llm.invoke(prompt)

        # Verify we got a response
        assert response
        assert len(response.strip()) > 0

        # Verify usage was logged
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-3.5-turbo-instruct" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

    def test_langchain_completion_batch_non_streaming(self, langchain_llm, caplog):
        """Test LangChain batch completion (non-streaming) captures usage."""
        prompts = ["What is 2+2?", "Name a color", "Count to 3"]

        # Make batch LangChain call
        responses = langchain_llm.batch(prompts)

        # Verify we got responses
        assert len(responses) == len(prompts)
        for response in responses:
            assert response
            assert len(response.strip()) > 0

        # Verify usage was logged
        # OpenAI completions API processes multiple prompts in a single request,
        # so we should get 1 usage log, not 3
        usage_logs = [
            line
            for line in caplog.text.split("\n")
            if "[LLM costs] OpenAI usage →" in line
        ]
        assert (
            len(usage_logs) == 1
        )  # Should have exactly 1 usage log for batch completion

    # ========================================================================
    # LANGCHAIN CHAT TESTS - NON-STREAMING
    # ========================================================================

    def test_langchain_chat_non_streaming(self, langchain_chat_model, caplog):
        """Test LangChain ChatOpenAI (non-streaming) captures usage."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Hello, what's your name?")]

        # Make LangChain chat call
        response = langchain_chat_model.invoke(messages)

        # Verify we got a response
        assert response
        assert hasattr(response, "content")
        assert len(response.content.strip()) > 0

        # Verify usage was logged
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

    def test_langchain_chat_batch_non_streaming(self, langchain_chat_model, caplog):
        """Test LangChain ChatOpenAI batch (non-streaming) captures usage."""
        from langchain_core.messages import HumanMessage

        message_batches = [
            [HumanMessage(content="What is Python?")],
            [HumanMessage(content="What is JavaScript?")],
            [HumanMessage(content="What is Go?")],
        ]

        # Make batch LangChain chat call
        responses = langchain_chat_model.batch(message_batches)

        # Verify we got responses
        assert len(responses) == len(message_batches)
        for response in responses:
            assert response
            assert hasattr(response, "content")
            assert len(response.content.strip()) > 0

        # Verify usage was logged for each call
        usage_logs = [
            line
            for line in caplog.text.split("\n")
            if "[LLM costs] OpenAI usage →" in line
        ]
        assert len(usage_logs) >= 3  # Should have at least 3 usage logs

    # ========================================================================
    # LANGCHAIN CHAIN TESTS - NON-STREAMING
    # ========================================================================

    def test_langchain_chain_non_streaming(self, langchain_chat_model, caplog):
        """Test LangChain chain usage captures usage."""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        # Create a simple chain
        prompt = ChatPromptTemplate.from_messages(
            [("human", "Tell me a short fact about {topic}")]
        )

        chain = prompt | langchain_chat_model | StrOutputParser()

        # Invoke the chain
        response = chain.invoke({"topic": "space"})

        # Verify we got a response
        assert response
        assert len(response.strip()) > 0

        # Verify usage was logged
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text

    # ========================================================================
    # PAYLOAD STRUCTURE TESTS
    # ========================================================================

    def test_langchain_payload_structure_validation(self, langchain_chat_model, caplog):
        """Test that LangChain usage data has the expected structure."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="What is 1+1?")]
        response = langchain_chat_model.invoke(messages)

        # Verify the response structure
        assert response
        assert hasattr(response, "content")
        assert hasattr(response, "response_metadata")

        # Verify usage was logged with proper format
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
