"""
Dedicated tests for LangChain streaming usage tracking and cost event integration.

Focus: Streaming LangChain API calls using OpenAI LLM wrapper.
"""

import sys
from pathlib import Path

import openai
import pytest
from environs import Env

# Add the parent directory to sys.path so we can import from the main project
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider
from llmcosts.tracker.frameworks import Framework

# Load environment variables from .env file in the tests directory
env = Env()
env.read_env(Path(__file__).parent / ".env")


class TestLangChainStreaming:
    """Test suite for LLMTrackingProxy with LangChain streaming calls."""

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
    def langchain_llm(self, tracked_openai_client):
        """Create a LangChain OpenAI LLM using a tracked approach (streaming)."""
        try:
            from langchain_openai import OpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Pass the tracked completions client to LangChain
        return OpenAI(
            client=tracked_openai_client.completions,
            model="gpt-3.5-turbo-instruct",
            max_tokens=50,
            temperature=0.1,
            streaming=True,  # Enable streaming
        )

    @pytest.fixture
    def langchain_chat_model(self, tracked_openai_client):
        """Create a LangChain ChatOpenAI model using a tracked approach (streaming)."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Pass the tracked chat completions client to LangChain
        return ChatOpenAI(
            client=tracked_openai_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=50,
            temperature=0.1,
            streaming=True,  # Enable streaming
        )

    # ========================================================================
    # LANGCHAIN COMPLETION TESTS - STREAMING
    # ========================================================================

    def test_langchain_completion_streaming(self, langchain_llm, caplog):
        """Test LangChain completion (streaming) captures usage."""
        prompt = "Count from 1 to 5"

        # Make LangChain streaming call
        response_chunks = []
        for chunk in langchain_llm.stream(prompt):
            response_chunks.append(chunk)

        # Verify we got chunks
        assert len(response_chunks) > 0

        # Combine all chunks to verify content
        full_response = "".join(response_chunks)
        assert len(full_response.strip()) > 0

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

    def test_langchain_completion_streaming_with_callback(
        self, tracked_openai_client, caplog
    ):
        """Test LangChain completion streaming with callback handler."""
        try:
            from langchain.callbacks.streaming_stdout import (
                StreamingStdOutCallbackHandler,
            )
            from langchain_openai import OpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Create LangChain LLM with streaming callback
        langchain_llm = OpenAI(
            client=tracked_openai_client.completions,
            model="gpt-3.5-turbo-instruct",
            max_tokens=30,
            temperature=0.1,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
        )

        prompt = "Say hello"

        # Make LangChain call with callback
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

    # ========================================================================
    # LANGCHAIN CHAT TESTS - STREAMING
    # ========================================================================

    def test_langchain_chat_streaming(self, langchain_chat_model, caplog):
        """Test LangChain ChatOpenAI (streaming) captures usage."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Count from 1 to 5")]

        # Make LangChain streaming chat call
        response_chunks = []
        for chunk in langchain_chat_model.stream(messages):
            response_chunks.append(chunk)

        # Verify we got chunks
        assert len(response_chunks) > 0

        # Combine all chunks to verify content
        full_response = "".join(
            [chunk.content for chunk in response_chunks if chunk.content]
        )
        assert len(full_response.strip()) > 0

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

    def test_langchain_chat_streaming_with_callback(
        self, tracked_openai_client, caplog
    ):
        """Test LangChain ChatOpenAI streaming with callback handler."""
        try:
            from langchain.callbacks.streaming_stdout import (
                StreamingStdOutCallbackHandler,
            )
            from langchain_core.messages import HumanMessage
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Create LangChain ChatOpenAI with streaming callback
        langchain_chat_model = ChatOpenAI(
            client=tracked_openai_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=30,
            temperature=0.1,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
        )

        messages = [HumanMessage(content="Say hello")]

        # Make LangChain call with callback
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

    # ========================================================================
    # LANGCHAIN CHAIN TESTS - STREAMING
    # ========================================================================

    def test_langchain_chain_streaming(self, langchain_chat_model, caplog):
        """Test LangChain chain usage with streaming captures usage."""
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate

        # Create a simple chain
        prompt = ChatPromptTemplate.from_messages(
            [("human", "Count from 1 to {number}")]
        )

        chain = prompt | langchain_chat_model | StrOutputParser()

        # Stream the chain
        response_chunks = []
        for chunk in chain.stream({"number": "3"}):
            response_chunks.append(chunk)

        # Verify we got chunks
        assert len(response_chunks) > 0

        # Combine all chunks to verify content
        full_response = "".join(response_chunks)
        assert len(full_response.strip()) > 0

        # Verify usage was logged
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text

    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================

    def test_langchain_streaming_validation_requirements(
        self, tracked_openai_client, caplog
    ):
        """Test that LangChain streaming with OpenAI still respects stream_options requirements."""
        try:
            from langchain_core.messages import HumanMessage
            from langchain_openai import ChatOpenAI
        except ImportError:
            pytest.skip("langchain-openai not installed")

        # Create LangChain ChatOpenAI with streaming
        langchain_chat_model = ChatOpenAI(
            client=tracked_openai_client.chat.completions,
            model="gpt-4o-mini",
            max_tokens=30,
            temperature=0.1,
            streaming=True,
        )

        messages = [HumanMessage(content="Hello")]

        # This should work because LangChain handles the stream_options internally
        response_chunks = []
        for chunk in langchain_chat_model.stream(messages):
            response_chunks.append(chunk)

        # Verify we got chunks
        assert len(response_chunks) > 0

        # Verify usage was logged
        assert "[LLM costs] OpenAI usage →" in caplog.text

    # ========================================================================
    # PAYLOAD STRUCTURE TESTS
    # ========================================================================

    def test_langchain_streaming_payload_structure(self, langchain_chat_model, caplog):
        """Test that LangChain streaming usage data has the expected structure."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Count to 3")]

        # Make streaming call
        response_chunks = list(langchain_chat_model.stream(messages))

        # Verify we got chunks
        assert len(response_chunks) > 0

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

    def test_langchain_streaming_chunk_structure(self, langchain_chat_model):
        """Test that LangChain streaming chunks have the expected structure."""
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Hello")]

        # Make streaming call
        response_chunks = list(langchain_chat_model.stream(messages))

        # Verify we got chunks
        assert len(response_chunks) > 0

        # Verify chunk structure
        for chunk in response_chunks:
            assert hasattr(chunk, "content")
            # Content can be empty string for some chunks
            assert chunk.content is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
