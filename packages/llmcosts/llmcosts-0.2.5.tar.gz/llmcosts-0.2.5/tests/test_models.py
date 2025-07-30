"""
Tests for models API functions - makes real API calls to test functionality.

Focus: Testing the models endpoint SDK functions with real API responses.
"""

import os

import pytest
from environs import Env

from llmcosts.models import (
    get_models_by_provider,
    get_models_dict,
    get_providers_by_model,
    is_model_supported,
    list_models,
)
from llmcosts.tracker import Provider

# Load environment variables
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))


class TestModelsEndpointReal:
    """Test models endpoint functions with real API calls."""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment or skip test."""
        api_key = env.str("LLMCOSTS_API_KEY", None)
        if not api_key:
            pytest.skip(
                "LLMCOSTS_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )
        return api_key

    def test_list_models_basic(self, api_key):
        """Test basic list_models functionality with real API."""
        models = list_models(api_key=api_key)

        # Verify we got a list
        assert isinstance(models, list)
        assert len(models) > 0

        # Check structure of first model
        first_model = models[0]
        assert "provider" in first_model
        assert "model_id" in first_model
        assert "aliases" in first_model

        # Verify data types
        assert isinstance(first_model["provider"], str)
        assert isinstance(first_model["model_id"], str)
        assert isinstance(first_model["aliases"], list)

        print(f"✅ Found {len(models)} models")

    def test_get_models_dict_structure(self, api_key):
        """Test get_models_dict returns proper structure."""
        models_dict = get_models_dict(api_key=api_key)

        # Verify it's a dictionary
        assert isinstance(models_dict, dict)
        assert len(models_dict) > 0

        # Check that each key is a provider with models
        for provider, models in models_dict.items():
            assert isinstance(provider, str)
            assert isinstance(models, list)
            assert len(models) > 0

            # Check first model structure
            first_model = models[0]
            assert "provider" in first_model
            assert "model_id" in first_model
            assert "aliases" in first_model
            assert first_model["provider"] == provider

        print(f"✅ Found {len(models_dict)} providers: {list(models_dict.keys())}")

    def test_get_models_by_provider_openai(self, api_key):
        """Test getting models for OpenAI provider."""
        # Test with enum
        openai_models_enum = get_models_by_provider(Provider.OPENAI, api_key=api_key)
        assert isinstance(openai_models_enum, list)

        # Test with string
        openai_models_str = get_models_by_provider("openai", api_key=api_key)
        assert isinstance(openai_models_str, list)

        # Should be the same
        assert openai_models_enum == openai_models_str

        # Should contain some GPT models
        model_string = " ".join(openai_models_enum).lower()
        assert any(term in model_string for term in ["gpt", "o1", "o3"])

        print(f"✅ Found {len(openai_models_enum)} OpenAI models")

    def test_get_models_by_provider_anthropic(self, api_key):
        """Test getting models for Anthropic provider."""
        anthropic_models = get_models_by_provider(Provider.ANTHROPIC, api_key=api_key)
        assert isinstance(anthropic_models, list)

        # Should contain Claude models
        model_string = " ".join(anthropic_models).lower()
        assert "claude" in model_string

        print(f"✅ Found {len(anthropic_models)} Anthropic models")

    def test_get_models_by_provider_nonexistent(self, api_key):
        """Test getting models for nonexistent provider."""
        result = get_models_by_provider("nonexistent-provider", api_key=api_key)
        assert result == []

    def test_get_models_by_provider_case_insensitive(self, api_key):
        """Test that provider matching is case insensitive."""
        openai_lower = get_models_by_provider("openai", api_key=api_key)
        openai_upper = get_models_by_provider("OPENAI", api_key=api_key)
        openai_mixed = get_models_by_provider("OpenAI", api_key=api_key)

        assert openai_lower == openai_upper == openai_mixed

    def test_get_providers_by_model_gpt4(self, api_key):
        """Test getting providers that support GPT-4."""
        providers = get_providers_by_model("gpt-4", api_key=api_key)
        assert isinstance(providers, list)

        # Should at least include OpenAI
        assert "openai" in providers

        print(f"✅ GPT-4 supported by: {providers}")

    def test_get_providers_by_model_claude(self, api_key):
        """Test getting providers for Claude models."""
        # Try different Claude model identifiers
        claude_variants = [
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
        ]

        found_providers = False
        for model in claude_variants:
            providers = get_providers_by_model(model, api_key=api_key)
            if providers:
                assert "anthropic" in providers
                found_providers = True
                print(f"✅ {model} supported by: {providers}")
                break

        assert found_providers, "Should find at least one Claude model"

    def test_get_providers_by_model_nonexistent(self, api_key):
        """Test getting providers for nonexistent model."""
        providers = get_providers_by_model(
            "definitely-not-a-real-model-12345", api_key=api_key
        )
        assert providers == []

    def test_is_model_supported_openai_gpt4(self, api_key):
        """Test checking if OpenAI supports GPT-4."""
        # Test with enum
        supported_enum = is_model_supported(Provider.OPENAI, "gpt-4", api_key=api_key)
        assert supported_enum is True

        # Test with string
        supported_str = is_model_supported("openai", "gpt-4", api_key=api_key)
        assert supported_str is True

    def test_is_model_supported_anthropic_claude(self, api_key):
        """Test checking if Anthropic supports Claude models."""
        # Try a few different Claude models
        claude_models = [
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022",
        ]

        found_supported = False
        for model in claude_models:
            if is_model_supported(Provider.ANTHROPIC, model, api_key=api_key):
                found_supported = True
                print(f"✅ Anthropic supports {model}")
                break

        assert found_supported, "Should find at least one supported Claude model"

    def test_is_model_supported_false_cases(self, api_key):
        """Test cases where is_model_supported should return False."""
        # Wrong provider for model
        assert is_model_supported("anthropic", "gpt-4", api_key=api_key) is False
        assert (
            is_model_supported("openai", "claude-3-sonnet-20240229", api_key=api_key)
            is False
        )

        # Nonexistent model
        assert (
            is_model_supported("openai", "definitely-not-real", api_key=api_key)
            is False
        )

        # Nonexistent provider
        assert is_model_supported("fake-provider", "gpt-4", api_key=api_key) is False

    def test_is_model_supported_case_insensitive(self, api_key):
        """Test that provider matching is case insensitive."""
        result_lower = is_model_supported("openai", "gpt-4", api_key=api_key)
        result_upper = is_model_supported("OPENAI", "gpt-4", api_key=api_key)
        result_mixed = is_model_supported("OpenAI", "gpt-4", api_key=api_key)

        assert result_lower == result_upper == result_mixed

    def test_aliases_functionality(self, api_key):
        """Test that model aliases work correctly."""
        models = list_models(api_key=api_key)

        # Find a model with aliases
        model_with_aliases = None
        for model in models:
            if model.get("aliases") and len(model["aliases"]) > 0:
                model_with_aliases = model
                break

        if model_with_aliases:
            provider = model_with_aliases["provider"]
            model_id = model_with_aliases["model_id"]
            alias = model_with_aliases["aliases"][0]

            # Test that both model_id and alias work
            providers_by_id = get_providers_by_model(model_id, api_key=api_key)
            providers_by_alias = get_providers_by_model(alias, api_key=api_key)

            assert provider in providers_by_id
            assert provider in providers_by_alias

            # Test is_model_supported with alias
            assert is_model_supported(provider, model_id, api_key=api_key) is True
            assert is_model_supported(provider, alias, api_key=api_key) is True

            print(f"✅ Alias test passed: {model_id} has alias {alias}")

    def test_provider_enum_consistency(self, api_key):
        """Test that Provider enum values match actual providers."""
        models_dict = get_models_dict(api_key=api_key)
        available_providers = set(models_dict.keys())

        # Test some common Provider enum values
        enum_tests = [
            (Provider.OPENAI, "openai"),
            (Provider.ANTHROPIC, "anthropic"),
            (Provider.GOOGLE, "google"),
            (Provider.AMAZON_BEDROCK, "amazon-bedrock"),
        ]

        for provider_enum, expected_string in enum_tests:
            if expected_string in available_providers:
                models_enum = get_models_by_provider(provider_enum, api_key=api_key)
                models_string = get_models_by_provider(expected_string, api_key=api_key)
                assert models_enum == models_string
                print(f"✅ Provider enum consistency verified for {expected_string}")

    def test_comprehensive_integration(self, api_key):
        """Comprehensive test that verifies all functions work together."""
        # Get all models
        all_models = list_models(api_key=api_key)
        assert len(all_models) > 0

        # Convert to dict
        models_dict = get_models_dict(api_key=api_key)

        # Verify the dict contains all models
        total_models_in_dict = sum(len(models) for models in models_dict.values())
        assert total_models_in_dict == len(all_models)

        # Test a few provider/model combinations
        test_count = 0
        for provider, models in models_dict.items():
            if test_count >= 3:  # Limit tests to avoid too many API calls
                break

            if models:  # Only test if provider has models
                model_id = models[0]["model_id"]

                # Test get_models_by_provider
                provider_models = get_models_by_provider(provider, api_key=api_key)
                assert model_id in provider_models

                # Test get_providers_by_model
                model_providers = get_providers_by_model(model_id, api_key=api_key)
                assert provider in model_providers

                # Test is_model_supported
                assert is_model_supported(provider, model_id, api_key=api_key) is True

                test_count += 1

        print(
            f"✅ Comprehensive integration test passed for {test_count} provider/model combinations"
        )


class TestModelsEndpointErrors:
    """Test error handling for models endpoint functions."""

    def test_no_api_key_with_env_cleared(self):
        """Test behavior when no API key is provided and none in environment."""
        # Temporarily remove any environment API key
        original_key = os.environ.get("LLMCOSTS_API_KEY")
        if original_key:
            del os.environ["LLMCOSTS_API_KEY"]

        try:
            # Should raise ValueError for missing API key
            with pytest.raises(ValueError, match="LLMCOSTS_API_KEY is required"):
                list_models()
        finally:
            # Restore original key if it existed
            if original_key:
                os.environ["LLMCOSTS_API_KEY"] = original_key

    def test_models_endpoint_requires_authentication(self):
        """Test that models endpoint properly rejects invalid API keys."""
        import requests

        # Test with invalid API key should get 401 Unauthorized
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            list_models(api_key="invalid-api-key-12345")

        # Should be a 401 Unauthorized error
        assert "401" in str(exc_info.value)
        assert "Unauthorized" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
