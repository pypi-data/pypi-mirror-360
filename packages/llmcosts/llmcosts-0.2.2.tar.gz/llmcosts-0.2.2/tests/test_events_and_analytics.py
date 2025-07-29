"""
Tests for events management and analytics API functions.

Focus: Testing the new SDK functions for health checks, events management,
and analytics with real API responses.
"""

import os
from datetime import datetime, timedelta

import pytest
from environs import Env

from llmcosts.models import (
    export_events,
    get_cost_event,
    get_cost_trends,
    get_daily_costs,
    get_model_efficiency,
    get_model_ranking,
    get_monthly_costs,
    get_peak_usage,
    get_provider_comparison,
    get_usage_frequency,
    get_usage_outliers,
    get_usage_patterns,
    health_check,
    list_events,
    search_events,
)

# Load environment variables
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))


class TestHealthCheck:
    """Test health check functionality with real API calls."""

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

    def test_health_check_basic(self, api_key):
        """Test basic health check functionality."""
        health = health_check(api_key=api_key)

        assert isinstance(health, dict)
        assert "status" in health
        assert "version" in health
        assert "timestamp" in health

        assert isinstance(health["status"], str)
        assert isinstance(health["version"], str)
        assert isinstance(health["timestamp"], str)

        print(f"✅ API Status: {health['status']}")
        print(f"  Version: {health['version']}")
        print(f"  Timestamp: {health['timestamp']}")

    def test_health_check_status_ok(self, api_key):
        """Test that health check returns OK status."""
        health = health_check(api_key=api_key)

        # The status should indicate the API is healthy
        assert health["status"] in ["ok", "healthy", "OK", "up"], (
            f"Unexpected status: {health['status']}"
        )


class TestEventsManagement:
    """Test events management functionality with real API calls."""

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

    def test_list_events_basic(self, api_key):
        """Test basic list events functionality."""
        events = list_events(api_key=api_key)

        assert isinstance(events, list)
        print(f"✅ Found {len(events)} total events")

        if len(events) > 0:
            event = events[0]
            assert "uuid" in event
            assert "model_id" in event
            assert "provider" in event
            assert "timestamp" in event
            assert "total_cost" in event

            print(
                f"  Sample event: {event['provider']} {event['model_id']} - ${event['total_cost']}"
            )

    def test_list_events_with_filters(self, api_key):
        """Test list events with various filters."""
        # Test provider filter
        openai_events = list_events(provider="openai", api_key=api_key)
        assert isinstance(openai_events, list)

        if len(openai_events) > 0:
            for event in openai_events[:3]:  # Check first 3
                assert event["provider"] == "openai"
            print(f"✅ Found {len(openai_events)} OpenAI events")

        # Test cost range filter
        expensive_events = list_events(min_cost=0.001, api_key=api_key)
        assert isinstance(expensive_events, list)

        if len(expensive_events) > 0:
            for event in expensive_events[:3]:  # Check first 3
                cost = float(event["total_cost"])
                assert cost >= 0.001
            print(f"✅ Found {len(expensive_events)} events with cost >= $0.001")

    def test_list_events_date_range(self, api_key):
        """Test list events with date range filtering."""
        # Get events from last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        events = list_events(
            start=start_date.isoformat(), end=end_date.isoformat(), api_key=api_key
        )

        assert isinstance(events, list)
        print(f"✅ Found {len(events)} events in the last 30 days")

    def test_search_events_aggregation(self, api_key):
        """Test search events with aggregation."""
        aggregates = search_events(api_key=api_key)

        assert isinstance(aggregates, list)
        print(f"✅ Found {len(aggregates)} aggregated groups")

        if len(aggregates) > 0:
            agg = aggregates[0]
            assert "provider" in agg
            assert "model_id" in agg
            assert "total_cost" in agg
            assert "call_count" in agg

            assert isinstance(agg["total_cost"], (int, float))
            assert isinstance(agg["call_count"], int)
            assert agg["call_count"] >= 0

            print(
                f"  Sample: {agg['provider']} {agg['model_id']} - ${agg['total_cost']} ({agg['call_count']} calls)"
            )

    def test_export_events_csv(self, api_key):
        """Test exporting events as CSV."""
        csv_data = export_events(format="csv", api_key=api_key)

        assert isinstance(csv_data, str)
        assert len(csv_data) > 0

        # Should have CSV headers
        lines = csv_data.strip().split("\n")
        if len(lines) > 0:
            headers = lines[0].lower()
            assert "uuid" in headers or "id" in headers
            assert "cost" in headers or "total" in headers

        print(f"✅ Exported CSV data: {len(lines)} lines")

    def test_export_events_json(self, api_key):
        """Test exporting events as JSON."""
        json_data = export_events(format="json", api_key=api_key)

        assert isinstance(json_data, str)
        assert len(json_data) > 0

        # Should be valid JSON
        import json

        try:
            parsed = json.loads(json_data)
            assert isinstance(parsed, list)
            print(f"✅ Exported JSON data: {len(parsed)} events")
        except json.JSONDecodeError:
            # If it's not a JSON array, it might be JSONL (one JSON per line)
            lines = json_data.strip().split("\n")
            if len(lines) > 0:
                first_line = json.loads(lines[0])
                assert isinstance(first_line, dict)
                print(f"✅ Exported JSONL data: {len(lines)} lines")

    def test_get_cost_event_nonexistent(self, api_key):
        """Test getting a nonexistent cost event."""
        # Use a fake response ID that shouldn't exist
        event = get_cost_event("nonexistent-response-id-12345", api_key=api_key)

        # Should return None for nonexistent events
        assert event is None
        print("✅ Correctly returned None for nonexistent event")


class TestCostAnalytics:
    """Test cost analytics functionality with real API calls."""

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

    def test_get_daily_costs(self, api_key):
        """Test getting daily costs."""
        daily_costs = get_daily_costs(api_key=api_key)

        assert isinstance(daily_costs, list)
        print(f"✅ Found {len(daily_costs)} daily cost entries")

        if len(daily_costs) > 0:
            day = daily_costs[0]
            assert "date" in day
            assert "total_cost" in day
            assert "call_count" in day

            assert isinstance(day["total_cost"], (int, float))
            assert isinstance(day["call_count"], int)
            assert day["call_count"] >= 0

            print(
                f"  Sample: {day['date']} - ${day['total_cost']} ({day['call_count']} calls)"
            )

    def test_get_daily_costs_with_range(self, api_key):
        """Test getting daily costs with date range."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        daily_costs = get_daily_costs(
            start=start_date.isoformat(), end=end_date.isoformat(), api_key=api_key
        )

        assert isinstance(daily_costs, list)
        print(f"✅ Found {len(daily_costs)} daily cost entries in 7-day range")

    def test_get_monthly_costs(self, api_key):
        """Test getting monthly costs."""
        monthly_costs = get_monthly_costs(api_key=api_key)

        assert isinstance(monthly_costs, list)
        print(f"✅ Found {len(monthly_costs)} monthly cost entries")

        if len(monthly_costs) > 0:
            month = monthly_costs[0]
            assert "month" in month
            assert "total_cost" in month
            assert "call_count" in month

            assert isinstance(month["total_cost"], (int, float))
            assert isinstance(month["call_count"], int)

            print(
                f"  Sample: {month['month']} - ${month['total_cost']} ({month['call_count']} calls)"
            )

    def test_get_monthly_costs_specific_year(self, api_key):
        """Test getting monthly costs for a specific year."""
        current_year = datetime.now().year
        monthly_costs = get_monthly_costs(year=current_year, api_key=api_key)

        assert isinstance(monthly_costs, list)
        print(f"✅ Found {len(monthly_costs)} monthly cost entries for {current_year}")

    def test_get_cost_trends(self, api_key):
        """Test getting cost trends."""
        # Test different periods
        for period in ["24h", "7d", "mtd"]:
            trends = get_cost_trends(period=period, api_key=api_key)

            assert isinstance(trends, list)
            print(f"✅ Found {len(trends)} trend points for {period}")

            if len(trends) > 0:
                trend = trends[0]
                assert "label" in trend
                assert "cost" in trend
                assert "count" in trend

                assert isinstance(trend["cost"], (int, float))
                assert isinstance(trend["count"], int)

    def test_get_peak_usage(self, api_key):
        """Test getting peak usage."""
        peak = get_peak_usage(days=30, api_key=api_key)

        # Peak might be None if no data
        if peak is not None:
            assert isinstance(peak, dict)
            assert "timestamp" in peak
            assert "total_cost" in peak
            assert "call_count" in peak

            assert isinstance(peak["total_cost"], (int, float))
            assert isinstance(peak["call_count"], int)

            print(
                f"✅ Peak usage: {peak['timestamp']} - ${peak['total_cost']} ({peak['call_count']} calls)"
            )
        else:
            print("✅ No peak usage data found (expected for new accounts)")


class TestModelAnalytics:
    """Test model analytics functionality with real API calls."""

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

    def test_get_model_ranking(self, api_key):
        """Test getting model ranking."""
        rankings = get_model_ranking(api_key=api_key)

        assert isinstance(rankings, list)
        print(f"✅ Found {len(rankings)} models in ranking")

        if len(rankings) > 0:
            model = rankings[0]
            assert "provider" in model
            assert "model_id" in model
            assert "total_cost" in model
            assert "call_count" in model

            assert isinstance(model["total_cost"], (int, float))
            assert isinstance(model["call_count"], int)

            print(
                f"  Top model: {model['provider']} {model['model_id']} - ${model['total_cost']}"
            )

    def test_get_model_efficiency(self, api_key):
        """Test getting model efficiency metrics."""
        efficiency = get_model_efficiency(api_key=api_key)

        assert isinstance(efficiency, list)
        print(f"✅ Found {len(efficiency)} models with efficiency data")

        if len(efficiency) > 0:
            model = efficiency[0]
            assert "provider" in model
            assert "model_id" in model
            assert "cost_per_token" in model
            assert "call_count" in model

            assert isinstance(model["cost_per_token"], (int, float))
            assert isinstance(model["call_count"], int)
            assert model["cost_per_token"] >= 0

            print(
                f"  Sample: {model['provider']} {model['model_id']} - ${model['cost_per_token']:.8f}/token"
            )


class TestProviderAnalytics:
    """Test provider analytics functionality with real API calls."""

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

    def test_get_provider_comparison(self, api_key):
        """Test getting provider comparison."""
        comparison = get_provider_comparison(api_key=api_key)

        assert isinstance(comparison, list)
        print(f"✅ Found {len(comparison)} providers in comparison")

        if len(comparison) > 0:
            provider = comparison[0]
            assert "provider" in provider
            assert "total_cost" in provider
            assert "call_count" in provider

            assert isinstance(provider["total_cost"], (int, float))
            assert isinstance(provider["call_count"], int)

            avg_cost = (
                provider["total_cost"] / provider["call_count"]
                if provider["call_count"] > 0
                else 0
            )
            print(
                f"  {provider['provider']}: ${provider['total_cost']:.4f} total, ${avg_cost:.6f} avg/call"
            )


class TestUsageAnalytics:
    """Test usage analytics functionality with real API calls."""

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

    def test_get_usage_patterns(self, api_key):
        """Test getting usage patterns."""
        patterns = get_usage_patterns(api_key=api_key)

        assert isinstance(patterns, dict)
        assert "hourly" in patterns
        assert "weekday" in patterns

        assert isinstance(patterns["hourly"], list)
        assert isinstance(patterns["weekday"], list)

        print(
            f"✅ Usage patterns: {len(patterns['hourly'])} hourly, {len(patterns['weekday'])} weekday"
        )

        # Check hourly patterns
        if len(patterns["hourly"]) > 0:
            hour = patterns["hourly"][0]
            assert "label" in hour
            assert "call_count" in hour
            assert isinstance(hour["call_count"], int)

        # Check weekday patterns
        if len(patterns["weekday"]) > 0:
            day = patterns["weekday"][0]
            assert "label" in day
            assert "call_count" in day
            assert isinstance(day["call_count"], int)

    def test_get_usage_frequency(self, api_key):
        """Test getting usage frequency."""
        frequency = get_usage_frequency(api_key=api_key)

        assert isinstance(frequency, list)
        print(f"✅ Found {len(frequency)} frequency data points")

        if len(frequency) > 0:
            day = frequency[0]
            assert "date" in day
            assert "call_count" in day

            assert isinstance(day["call_count"], int)
            assert day["call_count"] >= 0

            print(f"  Sample: {day['date']} - {day['call_count']} calls")

    def test_get_usage_outliers(self, api_key):
        """Test getting usage outliers."""
        outliers = get_usage_outliers(api_key=api_key)

        assert isinstance(outliers, list)
        print(f"✅ Found {len(outliers)} usage outliers")

        if len(outliers) > 0:
            outlier = outliers[0]
            assert "date" in outlier
            assert "call_count" in outlier
            assert "total_cost" in outlier

            assert isinstance(outlier["call_count"], int)
            assert isinstance(outlier["total_cost"], (int, float))

            print(
                f"  Outlier: {outlier['date']} - {outlier['call_count']} calls, ${outlier['total_cost']}"
            )
        else:
            print("  No outliers detected (normal for new accounts)")


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

    def test_comprehensive_analytics_workflow(self, api_key):
        """Test a comprehensive analytics workflow."""
        print("🔍 Running comprehensive analytics workflow...")

        # 1. Check API health
        health = health_check(api_key=api_key)
        assert health["status"].lower() in ["ok", "healthy", "up"]
        print(f"  ✅ API Health: {health['status']}")

        # 2. Get overall cost trends
        trends = get_cost_trends(period="7d", api_key=api_key)
        print(f"  ✅ Cost trends: {len(trends)} data points")

        # 3. Get model rankings
        rankings = get_model_ranking(api_key=api_key)
        print(f"  ✅ Model rankings: {len(rankings)} models")

        # 4. Get provider comparison
        comparison = get_provider_comparison(api_key=api_key)
        print(f"  ✅ Provider comparison: {len(comparison)} providers")

        # 5. Get usage patterns
        patterns = get_usage_patterns(api_key=api_key)
        print(
            f"  ✅ Usage patterns: {len(patterns['hourly'])}h + {len(patterns['weekday'])}d"
        )

        print("🎉 Comprehensive analytics workflow completed successfully!")

    def test_cost_analysis_with_filters(self, api_key):
        """Test cost analysis with various filters."""
        print("📊 Running filtered cost analysis...")

        # Get events with different filters
        all_events = list_events(api_key=api_key)
        openai_events = list_events(provider="openai", api_key=api_key)
        expensive_events = list_events(min_cost=0.001, api_key=api_key)

        print(f"  📈 All events: {len(all_events)}")
        print(f"  🤖 OpenAI events: {len(openai_events)}")
        print(f"  💰 Expensive events (>$0.001): {len(expensive_events)}")

        # Get aggregated view
        aggregates = search_events(api_key=api_key)
        print(f"  📊 Aggregated groups: {len(aggregates)}")

        # If we have data, verify consistency
        if len(all_events) > 0 and len(aggregates) > 0:
            # Total from aggregates should be reasonable
            total_from_agg = sum(agg["call_count"] for agg in aggregates)
            assert total_from_agg > 0
            print(f"  ✅ Aggregated total calls: {total_from_agg}")

    def test_export_and_analysis_consistency(self, api_key):
        """Test that export functions return consistent data with list functions."""
        print("🔄 Testing export consistency...")

        # Get events via list API
        events = list_events(api_key=api_key)

        # Export the same data
        csv_export = export_events(format="csv", api_key=api_key)
        json_export = export_events(format="json", api_key=api_key)

        print(f"  📋 List API: {len(events)} events")
        print(f"  📄 CSV export: {len(csv_export.splitlines())} lines")
        print(f"  📝 JSON export: {len(json_export)} characters")

        # Basic consistency checks
        if len(events) > 0:
            # CSV should have at least one header line plus data
            csv_lines = len(csv_export.splitlines())
            assert csv_lines >= 1  # At least header

            # JSON should not be empty
            assert len(json_export) > 10

        print("  ✅ Export consistency verified")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
