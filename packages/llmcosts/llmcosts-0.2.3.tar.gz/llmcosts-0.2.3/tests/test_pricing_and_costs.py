"""
Tests for pricing, token mapping, and cost calculation API functions.

Focus: Testing the new SDK functions for pricing, token mappings, and cost calculations
with real API responses.
"""

import os

import pytest
from environs import Env

from llmcosts.models import (
    calculate_cost_from_tokens,
    calculate_cost_from_usage,
    get_model_pricing,
    get_provider_token_mappings,
    get_token_mappings,
    list_models,
)
from llmcosts.tracker import Provider

# Load environment variables
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))


class TestModelPricing:
    """Test model pricing functionality with real API calls."""

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

    def test_get_model_pricing_openai_gpt4o_mini(self, api_key):
        """Test getting pricing for OpenAI GPT-4o mini."""
        pricing = get_model_pricing(Provider.OPENAI, "gpt-4o-mini", api_key=api_key)

        assert pricing is not None
        assert pricing["provider"].lower() == "openai"
        assert pricing["model_id"] == "gpt-4o-mini"
        assert "costs" in pricing
        assert isinstance(pricing["costs"], list)
        assert len(pricing["costs"]) > 0

        # Check cost structure
        for cost in pricing["costs"]:
            assert "token_type" in cost
            assert "cost_per_million" in cost
            assert isinstance(cost["cost_per_million"], (int, float))
            assert cost["cost_per_million"] >= 0

        # Should have at least input and output costs
        token_types = [cost["token_type"] for cost in pricing["costs"]]
        assert "input" in token_types
        assert "output" in token_types

        print(f"✅ GPT-4o mini pricing: {len(pricing['costs'])} cost types")
        for cost in pricing["costs"]:
            print(f"  {cost['token_type']}: ${cost['cost_per_million']}/M tokens")

    def test_get_model_pricing_anthropic_claude(self, api_key):
        """Test getting pricing for Anthropic Claude models."""
        # Try a few different Claude models to find one that works
        claude_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

        found_pricing = None
        for model_id in claude_models:
            pricing = get_model_pricing(Provider.ANTHROPIC, model_id, api_key=api_key)
            if pricing:
                found_pricing = pricing
                break

        assert found_pricing is not None, (
            f"Should find pricing for at least one Claude model: {claude_models}"
        )

        assert found_pricing["provider"].lower() == "anthropic"
        assert "costs" in found_pricing
        assert len(found_pricing["costs"]) > 0

        print(f"✅ Claude pricing found for {found_pricing['model_id']}")
        for cost in found_pricing["costs"]:
            print(f"  {cost['token_type']}: ${cost['cost_per_million']}/M tokens")

    def test_get_model_pricing_with_alias(self, api_key):
        """Test getting pricing using model aliases."""
        # Get all models to find one with aliases
        models = list_models(api_key=api_key)
        model_with_alias = None

        for model in models:
            if model.get("aliases") and len(model["aliases"]) > 0:
                model_with_alias = model
                break

        if model_with_alias:
            provider = model_with_alias["provider"]
            model_id = model_with_alias["model_id"]
            alias = model_with_alias["aliases"][0]

            # Get pricing by model_id
            pricing_by_id = get_model_pricing(provider, model_id, api_key=api_key)

            # Get pricing by alias
            pricing_by_alias = get_model_pricing(provider, alias, api_key=api_key)

            # Should be the same
            assert pricing_by_id == pricing_by_alias
            print(f"✅ Alias test passed: {model_id} == {alias}")

    def test_get_model_pricing_nonexistent(self, api_key):
        """Test getting pricing for nonexistent model."""
        pricing = get_model_pricing(
            Provider.OPENAI, "definitely-not-a-real-model", api_key=api_key
        )
        assert pricing is None

    def test_get_model_pricing_wrong_provider(self, api_key):
        """Test getting pricing with wrong provider."""
        pricing = get_model_pricing(Provider.ANTHROPIC, "gpt-4o-mini", api_key=api_key)
        assert pricing is None

    def test_get_model_pricing_string_provider(self, api_key):
        """Test getting pricing with string provider name."""
        pricing_enum = get_model_pricing(
            Provider.OPENAI, "gpt-4o-mini", api_key=api_key
        )
        pricing_str = get_model_pricing("openai", "gpt-4o-mini", api_key=api_key)

        assert pricing_enum == pricing_str


class TestTokenMappings:
    """Test token mapping functionality with real API calls."""

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

    def test_get_token_mappings_all_providers(self, api_key):
        """Test getting token mappings for all providers."""
        mappings = get_token_mappings(api_key=api_key)

        assert isinstance(mappings, dict)
        assert "token_mappings" in mappings
        assert "supported_providers" in mappings
        assert isinstance(mappings["token_mappings"], list)
        assert isinstance(mappings["supported_providers"], list)
        assert len(mappings["supported_providers"]) > 0

        # Check token mapping structure
        for mapping in mappings["token_mappings"]:
            assert "normalized_name" in mapping
            assert "provider_aliases" in mapping
            assert "description" in mapping
            assert isinstance(mapping["provider_aliases"], list)

        print(f"✅ Found mappings for {len(mappings['supported_providers'])} providers")
        print(f"  Supported providers: {mappings['supported_providers']}")

    def test_get_token_mappings_specific_provider(self, api_key):
        """Test getting token mappings for a specific provider."""
        mappings = get_token_mappings(provider=Provider.OPENAI, api_key=api_key)

        assert isinstance(mappings, dict)
        assert "token_mappings" in mappings
        assert mappings.get("provider") == "openai"

        # Should have normalized token types
        normalized_names = [m["normalized_name"] for m in mappings["token_mappings"]]
        assert "input" in normalized_names
        assert "output" in normalized_names

        print(f"✅ OpenAI token mappings: {normalized_names}")

    def test_get_token_mappings_with_examples(self, api_key):
        """Test getting token mappings with examples."""
        mappings = get_token_mappings(
            provider=Provider.OPENAI, include_examples=True, api_key=api_key
        )

        assert "examples" in mappings
        assert isinstance(mappings["examples"], list)

        if len(mappings["examples"]) > 0:
            example = mappings["examples"][0]
            assert "provider" in example
            assert "raw_usage" in example
            assert "normalized_tokens" in example
            assert "explanation" in example

            print(f"✅ Found {len(mappings['examples'])} normalization examples")
            print(f"  Example: {example['explanation']}")

    def test_get_provider_token_mappings_openai(self, api_key):
        """Test getting token mappings for OpenAI specifically."""
        mappings = get_provider_token_mappings(Provider.OPENAI, api_key=api_key)

        assert isinstance(mappings, dict)
        assert "token_mappings" in mappings
        assert "examples" in mappings

        # Should have examples
        assert isinstance(mappings["examples"], list)

        if len(mappings["examples"]) > 0:
            example = mappings["examples"][0]
            assert example["provider"] == "openai"
            assert "raw_usage" in example
            assert "normalized_tokens" in example

            print(
                f"✅ OpenAI specific mappings with {len(mappings['examples'])} examples"
            )

    def test_get_provider_token_mappings_anthropic(self, api_key):
        """Test getting token mappings for Anthropic specifically."""
        mappings = get_provider_token_mappings(Provider.ANTHROPIC, api_key=api_key)

        assert isinstance(mappings, dict)
        assert "token_mappings" in mappings
        assert "examples" in mappings

        print(
            f"✅ Anthropic specific mappings with {len(mappings['examples'])} examples"
        )

    def test_get_provider_token_mappings_string_provider(self, api_key):
        """Test getting provider token mappings with string provider."""
        mappings_enum = get_provider_token_mappings(Provider.OPENAI, api_key=api_key)
        mappings_str = get_provider_token_mappings("openai", api_key=api_key)

        assert mappings_enum == mappings_str

    def test_get_provider_token_mappings_nonexistent(self, api_key):
        """Test getting token mappings for nonexistent provider."""
        with pytest.raises(Exception):  # Should get 404 or similar error
            get_provider_token_mappings("nonexistent-provider", api_key=api_key)


class TestCostCalculation:
    """Test cost calculation functionality with real API calls."""

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

    def test_calculate_cost_from_tokens_openai(self, api_key):
        """Test calculating cost from normalized token counts for OpenAI."""
        result = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            api_key=api_key,
        )

        assert isinstance(result, dict)
        assert result["provider"] == "openai"
        assert result["model_id"] == "gpt-4o-mini"
        assert result["model_found"] is True
        assert "tokens" in result
        assert "costs" in result

        # Check tokens structure
        tokens = result["tokens"]
        assert tokens["input"] == 1000
        assert tokens["output"] == 500

        # Check costs structure
        costs = result["costs"]
        assert "input_cost" in costs
        assert "output_cost" in costs
        assert "total_cost" in costs
        assert isinstance(costs["total_cost"], (int, float))
        assert costs["total_cost"] > 0

        print("✅ GPT-4o mini cost calculation:")
        print(f"  Input cost: ${costs['input_cost']}")
        print(f"  Output cost: ${costs['output_cost']}")
        print(f"  Total cost: ${costs['total_cost']}")

    def test_calculate_cost_from_tokens_with_explanation(self, api_key):
        """Test calculating cost with detailed explanations."""
        result = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            include_explanation=True,
            api_key=api_key,
        )

        assert "explanations" in result
        if result["explanations"]:
            assert isinstance(result["explanations"], list)

            for explanation in result["explanations"]:
                assert "token_type" in explanation
                assert "raw_count" in explanation
                assert "billable_count" in explanation
                assert "rate_per_million" in explanation
                assert "calculated_cost" in explanation
                assert "formula" in explanation

                print(
                    f"✅ Explanation for {explanation['token_type']}: {explanation['formula']}"
                )

    def test_calculate_cost_from_tokens_all_token_types(self, api_key):
        """Test calculating cost with all token types."""
        result = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            cache_read_tokens=100,
            cache_write_tokens=50,
            reasoning_tokens=200,
            tool_use_tokens=25,
            api_key=api_key,
        )

        tokens = result["tokens"]
        assert tokens["input"] == 1000
        assert tokens["output"] == 500
        assert tokens["cache_read"] == 100
        assert tokens["cache_write"] == 50
        assert tokens["reasoning"] == 200
        assert tokens["tool_use"] == 25

        print(
            f"✅ Cost calculation with all token types: ${result['costs']['total_cost']}"
        )

    def test_calculate_cost_from_usage_openai_format(self, api_key):
        """Test calculating cost from OpenAI-style usage data."""
        usage_data = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        }

        result = calculate_cost_from_usage(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            usage=usage_data,
            api_key=api_key,
        )

        assert isinstance(result, dict)
        assert result["provider"] == "openai"
        assert result["model_id"] == "gpt-4o-mini"
        assert result["model_found"] is True
        assert "costs" in result
        assert result["costs"]["total_cost"] > 0

        print(f"✅ Cost from OpenAI usage data: ${result['costs']['total_cost']}")

    def test_calculate_cost_from_usage_anthropic_format(self, api_key):
        """Test calculating cost from Anthropic-style usage data."""
        # Find a supported Claude model
        claude_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

        usage_data = {"input_tokens": 100, "output_tokens": 50}

        successful_model = None
        for model_id in claude_models:
            try:
                result = calculate_cost_from_usage(
                    provider=Provider.ANTHROPIC,
                    model_id=model_id,
                    usage=usage_data,
                    api_key=api_key,
                )
                if result.get("model_found"):
                    successful_model = model_id
                    print(
                        f"✅ Cost from Anthropic usage data ({model_id}): ${result['costs']['total_cost']}"
                    )
                    break
            except Exception as e:
                print(f"  Failed for {model_id}: {e}")
                continue

        # At least one should work
        assert successful_model is not None, (
            f"Should find at least one working Claude model from {claude_models}"
        )

    def test_calculate_cost_nonexistent_model(self, api_key):
        """Test calculating cost for nonexistent model."""
        result = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="definitely-not-a-real-model",
            input_tokens=1000,
            output_tokens=500,
            api_key=api_key,
        )

        assert result["model_found"] is False
        # Should still return a result structure but with warnings or zero costs

    def test_calculate_cost_string_provider(self, api_key):
        """Test calculating cost with string provider name."""
        result_enum = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            api_key=api_key,
        )

        result_str = calculate_cost_from_tokens(
            provider="openai",
            model_id="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
            api_key=api_key,
        )

        # Results should be the same
        assert result_enum["costs"]["total_cost"] == result_str["costs"]["total_cost"]

    def test_calculate_cost_zero_tokens(self, api_key):
        """Test calculating cost with zero tokens."""
        result = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=0,
            output_tokens=0,
            api_key=api_key,
        )

        assert result["costs"]["total_cost"] == 0

    def test_cost_calculation_consistency(self, api_key):
        """Test that cost calculations are consistent between methods."""
        # Calculate cost using normalized tokens
        result_tokens = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=100,
            output_tokens=50,
            api_key=api_key,
        )

        # Calculate cost using OpenAI-style usage data
        usage_data = {
            "prompt_tokens": 100,  # Maps to input_tokens
            "completion_tokens": 50,  # Maps to output_tokens
            "total_tokens": 150,
        }

        result_usage = calculate_cost_from_usage(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            usage=usage_data,
            api_key=api_key,
        )

        # Total costs should be very close (allowing for small rounding differences)
        cost_tokens = float(result_tokens["costs"]["total_cost"])
        cost_usage = float(result_usage["costs"]["total_cost"])

        # Allow for small floating point differences
        assert abs(cost_tokens - cost_usage) < 0.000001, (
            f"Costs should be similar: {cost_tokens} vs {cost_usage}"
        )

        print(f"✅ Cost consistency verified: ${cost_tokens} ≈ ${cost_usage}")


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""

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

    def test_full_workflow_get_pricing_and_calculate(self, api_key):
        """Test complete workflow: get pricing, then calculate costs."""
        # Step 1: Get model pricing
        pricing = get_model_pricing(Provider.OPENAI, "gpt-4o-mini", api_key=api_key)
        assert pricing is not None

        # Step 2: Use the pricing information to understand costs
        input_cost_per_million = None
        output_cost_per_million = None

        for cost in pricing["costs"]:
            if cost["token_type"] == "input":
                input_cost_per_million = cost["cost_per_million"]
            elif cost["token_type"] == "output":
                output_cost_per_million = cost["cost_per_million"]

        assert input_cost_per_million is not None
        assert output_cost_per_million is not None

        # Step 3: Calculate actual costs
        result = calculate_cost_from_tokens(
            provider=Provider.OPENAI,
            model_id="gpt-4o-mini",
            input_tokens=1000000,  # 1 million tokens
            output_tokens=500000,  # 0.5 million tokens
            api_key=api_key,
        )

        # Step 4: Verify the calculation matches expected costs
        expected_input_cost = input_cost_per_million * 1.0  # 1M tokens
        expected_output_cost = output_cost_per_million * 0.5  # 0.5M tokens
        expected_total = expected_input_cost + expected_output_cost

        actual_total = float(result["costs"]["total_cost"])

        # Allow for small rounding differences
        assert abs(actual_total - expected_total) < 0.01, (
            f"Expected ~${expected_total}, got ${actual_total}"
        )

        print("✅ Full workflow verified:")
        print(f"  Expected total: ${expected_total}")
        print(f"  Actual total: ${actual_total}")

    def test_token_mapping_to_cost_calculation(self, api_key):
        """Test workflow: get token mappings, then use for cost calculation."""
        # Step 1: Get token mappings for OpenAI
        mappings = get_provider_token_mappings(Provider.OPENAI, api_key=api_key)

        # Step 2: Find an example of token normalization
        if len(mappings["examples"]) > 0:
            example = mappings["examples"][0]
            raw_usage = example["raw_usage"]
            normalized_tokens = example["normalized_tokens"]

            print("✅ Using example normalization:")
            print(f"  Raw usage: {raw_usage}")
            print(f"  Normalized: {normalized_tokens}")

            # Step 3: Calculate costs using both raw and normalized data
            # (This tests that the API handles both formats correctly)
            try:
                result_raw = calculate_cost_from_usage(
                    provider=Provider.OPENAI,
                    model_id="gpt-4o-mini",
                    usage=raw_usage,
                    api_key=api_key,
                )

                result_normalized = calculate_cost_from_tokens(
                    provider=Provider.OPENAI,
                    model_id="gpt-4o-mini",
                    input_tokens=normalized_tokens.get("input", 0),
                    output_tokens=normalized_tokens.get("output", 0),
                    api_key=api_key,
                )

                print(f"  Cost from raw usage: ${result_raw['costs']['total_cost']}")
                print(
                    f"  Cost from normalized: ${result_normalized['costs']['total_cost']}"
                )

            except Exception as e:
                print(f"  Note: Cost calculation test skipped due to: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
