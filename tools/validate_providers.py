#!/usr/bin/env python3
"""Validate providers.json against schema - CI/CD integration"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema package not installed")
    print("Run: pip install jsonschema")
    sys.exit(1)


def validate_providers_config():
    """Validate providers.json against schema"""
    base_dir = Path(__file__).resolve().parents[1]
    config_path = base_dir / "etc" / "providers.json"
    schema_path = base_dir / "etc" / "providers.schema.json"
    
    # Check files exist
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        return False
    
    if not schema_path.exists():
        print(f"ERROR: Schema file not found: {schema_path}")
        return False
    
    # Load files
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        with open(schema_path) as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        return False
    
    # Validate against schema
    try:
        jsonschema.validate(instance=config, schema=schema)
        print("✓ providers.json is valid")
    except jsonschema.ValidationError as e:
        print(f"ERROR: Schema validation failed:")
        print(f"  Path: {' -> '.join(str(p) for p in e.path)}")
        print(f"  Message: {e.message}")
        return False
    except jsonschema.SchemaError as e:
        print(f"ERROR: Invalid schema: {e}")
        return False
    
    # Additional semantic validation
    errors = []
    
    providers = config.get("providers", [])
    if not providers:
        errors.append("No providers defined")
    
    default_provider = config.get("default_provider")
    if not default_provider:
        errors.append("No default_provider specified")
    else:
        provider_ids = [p["id"] for p in providers]
        if default_provider not in provider_ids:
            errors.append(f"default_provider '{default_provider}' not found in providers")
    
    # Check for duplicate IDs
    provider_ids = [p["id"] for p in providers]
    duplicates = [pid for pid in provider_ids if provider_ids.count(pid) > 1]
    if duplicates:
        errors.append(f"Duplicate provider IDs: {set(duplicates)}")
    
    # Validate reasoning/settings consistency
    for provider in providers:
        pid = provider["id"]
        reasoning = provider["reasoning"]
        settings = provider["default_settings"]
        
        has_reasoning_effort = "reasoning_effort" in settings
        has_temperature = "temperature" in settings
        has_top_p = "top_p" in settings
        
        if reasoning:
            if not has_reasoning_effort:
                errors.append(f"{pid}: Reasoning model must have 'reasoning_effort'")
            if has_temperature or has_top_p:
                errors.append(f"{pid}: Reasoning model cannot have 'temperature' or 'top_p'")
        else:
            if has_reasoning_effort:
                errors.append(f"{pid}: Non-reasoning model cannot have 'reasoning_effort'")
            if not (has_temperature or has_top_p):
                errors.append(f"{pid}: Non-reasoning model must have 'temperature' or 'top_p'")
    
    if errors:
        print("ERROR: Semantic validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✓ Semantic validation passed")
    return True


if __name__ == "__main__":
    success = validate_providers_config()
    sys.exit(0 if success else 1)
