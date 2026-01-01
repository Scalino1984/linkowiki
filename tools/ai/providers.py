# tools/ai/providers.py
"""Provider management for PydanticAI v2 - STRICT CONFORMANCE"""
import json
import os
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator
import jsonschema


class ProviderConfig(BaseModel):
    """Configuration for a single AI provider/model - PydanticAI v2 compliant"""
    id: str
    provider: str
    model: str
    api_base: Optional[str] = None
    reasoning: bool
    env_key: str
    default_settings: Dict
    description: Optional[str] = None

    @field_validator('default_settings')
    @classmethod
    def validate_settings_structure(cls, v, info):
        """Validate settings match reasoning flag"""
        reasoning = info.data.get('reasoning', False)
        
        has_reasoning_effort = 'reasoning_effort' in v
        has_temperature = 'temperature' in v
        has_top_p = 'top_p' in v
        
        if reasoning:
            # Reasoning models: MUST have reasoning_effort, CANNOT have temperature/top_p
            if not has_reasoning_effort:
                raise ValueError(
                    f"Reasoning model must have 'reasoning_effort' in default_settings"
                )
            if has_temperature or has_top_p:
                raise ValueError(
                    f"Reasoning model cannot have 'temperature' or 'top_p' - only 'reasoning_effort' allowed"
                )
            if v['reasoning_effort'] not in ['low', 'medium', 'high']:
                raise ValueError(
                    f"reasoning_effort must be 'low', 'medium', or 'high'"
                )
        else:
            # Non-reasoning models: CANNOT have reasoning_effort
            if has_reasoning_effort:
                raise ValueError(
                    f"Non-reasoning model cannot have 'reasoning_effort' - use 'temperature' instead"
                )
            if not (has_temperature or has_top_p):
                raise ValueError(
                    f"Non-reasoning model must have at least 'temperature' or 'top_p'"
                )
        
        return v


class ProviderRegistry:
    """Registry for managing AI providers with strict validation"""
    
    def __init__(self, config_path: Path, schema_path: Path, default_provider_id: Optional[str] = None):
        self.config_path = config_path
        self.schema_path = schema_path
        self.providers: Dict[str, ProviderConfig] = {}
        self.default_provider_id: Optional[str] = default_provider_id
        self._load_and_validate()
    
    def _load_and_validate(self):
        """Load providers with JSON schema validation"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Provider config not found: {self.config_path}")
        
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Provider schema not found: {self.schema_path}")
        
        # Load JSON
        with open(self.config_path) as f:
            data = json.load(f)
        
        # Load schema
        with open(self.schema_path) as f:
            schema = json.load(f)
        
        # Validate against schema
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Provider configuration violates schema: {e.message}")
        
        # Parse providers
        for provider_data in data.get("providers", []):
            config = ProviderConfig(**provider_data)
            self.providers[config.id] = config
        
        # Set default provider
        if not self.default_provider_id:
            self.default_provider_id = data.get("default_provider")
        
        if not self.providers:
            raise ValueError("No providers configured")
        
        if self.default_provider_id not in self.providers:
            raise ValueError(f"Default provider '{self.default_provider_id}' not found in providers")
    
    def get_provider(self, provider_id: str) -> ProviderConfig:
        """Get provider config by ID"""
        if provider_id not in self.providers:
            available = ', '.join(self.providers.keys())
            raise ValueError(f"Unknown provider: {provider_id}. Available: {available}")
        return self.providers[provider_id]
    
    def get_default_provider(self) -> ProviderConfig:
        """Get default provider config"""
        return self.providers[self.default_provider_id]
    
    def list_providers(self) -> Dict[str, ProviderConfig]:
        """List all available providers"""
        return self.providers
    
    def validate_settings(self, provider_id: str, settings: Dict) -> None:
        """
        Validate model settings for provider type.
        Enforces STRICT PydanticAI v2 conformance rules.
        """
        provider = self.get_provider(provider_id)
        
        # Reasoning model rules
        if provider.reasoning:
            # MUST have reasoning_effort
            if 'reasoning_effort' not in settings:
                raise ValueError(
                    f"Reasoning model '{provider_id}' requires 'reasoning_effort' setting"
                )
            
            # CANNOT have temperature or top_p
            forbidden = [k for k in settings.keys() if k in ('temperature', 'top_p')]
            if forbidden:
                raise ValueError(
                    f"Reasoning model '{provider_id}' cannot use {forbidden}. "
                    f"Only 'reasoning_effort' is allowed."
                )
            
            # Validate reasoning_effort value
            if settings['reasoning_effort'] not in ['low', 'medium', 'high']:
                raise ValueError(
                    f"reasoning_effort must be 'low', 'medium', or 'high', "
                    f"got: {settings['reasoning_effort']}"
                )
        
        else:
            # Non-reasoning model rules
            # CANNOT have reasoning_effort
            if 'reasoning_effort' in settings:
                raise ValueError(
                    f"Non-reasoning model '{provider_id}' cannot use 'reasoning_effort'. "
                    f"Use 'temperature' instead."
                )
            
            # SHOULD have temperature or top_p
            if 'temperature' not in settings and 'top_p' not in settings:
                raise ValueError(
                    f"Non-reasoning model '{provider_id}' should have 'temperature' or 'top_p'"
                )
    
    def get_api_key(self, provider_id: str) -> str:
        """Get API key for provider from environment"""
        provider = self.get_provider(provider_id)
        api_key = os.getenv(provider.env_key)
        
        if not api_key:
            raise ValueError(
                f"API key not found. Set environment variable: {provider.env_key}"
            )
        
        return api_key


# Global registry instance
_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """Get or create global provider registry"""
    global _registry
    if _registry is None:
        from tools.config import get_config
        config = get_config()
        
        base_dir = Path(__file__).resolve().parents[2]
        config_path = base_dir / "etc" / "providers.json"
        schema_path = base_dir / "etc" / "providers.schema.json"
        
        _registry = ProviderRegistry(
            config_path=config_path,
            schema_path=schema_path,
            default_provider_id=config.default_provider
        )
    return _registry


def reset_provider_registry():
    """Reset global registry (for testing)"""
    global _registry
    _registry = None

