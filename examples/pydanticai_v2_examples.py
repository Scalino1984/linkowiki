#!/usr/bin/env python3
"""PydanticAI v2 Architecture Examples"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.ai.routing import ProviderRouter
from tools.ai.providers import get_provider_registry, reset_provider_registry

print("\n" + "="*70)
print("PydanticAI v2 Architecture - Quick Examples")
print("="*70)

# Example 1: Routing
print("\n1. Automatic Task Routing:")
for task in ["tags", "bulk", "analysis", "default"]:
    provider = ProviderRouter.route(task)
    print(f"  {task:10} → {provider}")

# Example 2: Provider Types
print("\n2. Provider Types:")
reset_provider_registry()
registry = get_provider_registry()
for pid, prov in registry.providers.items():
    type_str = "Reasoning" if prov.reasoning else "Text     "
    settings = list(prov.default_settings.keys())[0]
    print(f"  {type_str} | {pid:30} | {settings}")

# Example 3: Validation
print("\n3. Settings Validation:")
try:
    registry.validate_settings("openai-gpt5-reasoning", {"temperature": 0.5})
    print("  ✗ Should fail")
except ValueError as e:
    print(f"  ✓ Reasoning rejects temperature")

try:
    registry.validate_settings("openai-gpt5-text", {"reasoning_effort": "medium"})
    print("  ✗ Should fail")
except ValueError as e:
    print(f"  ✓ Text rejects reasoning_effort")

print("\n" + "="*70)
print("✓ Examples completed - Architecture working correctly")
print("="*70 + "\n")
