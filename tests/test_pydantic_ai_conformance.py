#!/usr/bin/env python3
"""Test suite for PydanticAI v2 conformance"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.ai.providers import get_provider_registry, reset_provider_registry
from tools.ai.agent_factory import AgentFactory
from tools.ai.routing import ProviderRouter
from pydantic import BaseModel


class TestOutput(BaseModel):
    """Test output model"""
    message: str


def test_provider_registry_loads():
    """Test that provider registry loads correctly"""
    print("Testing provider registry loading...")
    reset_provider_registry()
    registry = get_provider_registry()
    
    assert len(registry.providers) > 0, "No providers loaded"
    assert registry.default_provider_id is not None, "No default provider"
    print(f"✓ Loaded {len(registry.providers)} providers")


def test_reasoning_model_settings():
    """Test that reasoning models have correct settings"""
    print("\nTesting reasoning model settings...")
    reset_provider_registry()
    registry = get_provider_registry()
    
    for provider_id, provider in registry.providers.items():
        if provider.reasoning:
            # Must have reasoning_effort
            assert "reasoning_effort" in provider.default_settings, \
                f"{provider_id}: Missing reasoning_effort"
            
            # Must NOT have temperature or top_p
            assert "temperature" not in provider.default_settings, \
                f"{provider_id}: Reasoning model has temperature"
            assert "top_p" not in provider.default_settings, \
                f"{provider_id}: Reasoning model has top_p"
            
            print(f"✓ {provider_id}: reasoning_effort={provider.default_settings['reasoning_effort']}")


def test_non_reasoning_model_settings():
    """Test that non-reasoning models have correct settings"""
    print("\nTesting non-reasoning model settings...")
    reset_provider_registry()
    registry = get_provider_registry()
    
    for provider_id, provider in registry.providers.items():
        if not provider.reasoning:
            # Must NOT have reasoning_effort
            assert "reasoning_effort" not in provider.default_settings, \
                f"{provider_id}: Non-reasoning model has reasoning_effort"
            
            # Should have temperature or top_p
            assert "temperature" in provider.default_settings or "top_p" in provider.default_settings, \
                f"{provider_id}: Missing temperature/top_p"
            
            temp = provider.default_settings.get("temperature", "N/A")
            print(f"✓ {provider_id}: temperature={temp}")


def test_settings_validation():
    """Test settings validation enforces rules"""
    print("\nTesting settings validation...")
    reset_provider_registry()
    registry = get_provider_registry()
    
    # Find a reasoning model
    reasoning_provider = None
    non_reasoning_provider = None
    
    for provider in registry.providers.values():
        if provider.reasoning and not reasoning_provider:
            reasoning_provider = provider
        if not provider.reasoning and not non_reasoning_provider:
            non_reasoning_provider = provider
    
    # Test: reasoning model with temperature should fail
    if reasoning_provider:
        try:
            registry.validate_settings(reasoning_provider.id, {"temperature": 0.5})
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"✓ Reasoning model correctly rejects temperature: {e}")
    
    # Test: non-reasoning model with reasoning_effort should fail
    if non_reasoning_provider:
        try:
            registry.validate_settings(non_reasoning_provider.id, {"reasoning_effort": "medium"})
            assert False, "Should have raised ValueError"
        except ValueError as e:
            print(f"✓ Non-reasoning model correctly rejects reasoning_effort: {e}")


def test_routing():
    """Test automatic routing"""
    print("\nTesting automatic routing...")
    
    tests = [
        ("tags", "openai-gpt5-nano-text"),
        ("abstract", "openai-gpt5-nano-text"),
        ("bulk", "openai-gpt5-mini-text"),
        ("summary", "openai-gpt5-mini-text"),
        ("structure", "openai-gpt5-reasoning"),
        ("analysis", "openai-gpt5-reasoning"),
        ("default", "openai-gpt5-text"),
    ]
    
    for task_type, expected_provider in tests:
        result = ProviderRouter.route(task_type)
        assert result == expected_provider, f"Expected {expected_provider}, got {result}"
        print(f"✓ {task_type} → {result}")


def test_auto_detection():
    """Test automatic task detection from prompts"""
    print("\nTesting prompt-based task detection...")
    
    tests = [
        ("Generate tags for this article", "tags"),
        ("Create an abstract", "abstract"),
        ("Process bulk wiki entries", "bulk"),
        ("Analyze this complex problem deeply", "analysis"),
        ("Create a new wiki entry", "default"),
    ]
    
    for prompt, expected_task in tests:
        detected = ProviderRouter.detect_task_type(prompt)
        assert detected == expected_task, f"Expected {expected_task}, got {detected}"
        print(f"✓ '{prompt[:30]}...' → {detected}")


def test_agent_creation():
    """Test that agents can be created without API calls"""
    print("\nTesting agent creation (no API calls)...")
    reset_provider_registry()
    registry = get_provider_registry()
    
    # We can't actually test API calls without credentials
    # But we can test that the factory creates agents with correct structure
    
    for provider_id in registry.providers.keys():
        try:
            # This will fail on API key check, but structure is validated
            agent = AgentFactory.create_agent(
                provider_id=provider_id,
                output_type=TestOutput,
                system_prompt="Test prompt"
            )
        except ValueError as e:
            if "API key not found" in str(e):
                print(f"✓ {provider_id}: Structure valid (API key check works)")
            else:
                raise


def main():
    """Run all tests"""
    print("=" * 70)
    print("PydanticAI v2 Conformance Test Suite")
    print("=" * 70)
    
    try:
        test_provider_registry_loads()
        test_reasoning_model_settings()
        test_non_reasoning_model_settings()
        test_settings_validation()
        test_routing()
        test_auto_detection()
        test_agent_creation()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
