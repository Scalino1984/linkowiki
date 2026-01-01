# tools/ai/agent_factory.py
"""Agent factory for creating PydanticAI agents - STRICT v2 CONFORMANCE"""
from typing import Type, TypeVar, Optional, Sequence, Callable, Any
from pydantic import BaseModel
from pydantic_ai import Agent

from .providers import get_provider_registry, ProviderConfig


OutputT = TypeVar('OutputT')


class AgentFactory:
    """
    Factory for creating PydanticAI v2 compliant agents.
    
    RULES:
    - Reasoning models: only reasoning_effort in model_settings
    - Non-reasoning models: only temperature/top_p in model_settings
    - NO fallbacks, NO magic defaults
    - Settings validated at creation time
    """
    
    @staticmethod
    def create_agent(
        provider_id: str,
        output_type: Type[OutputT],
        system_prompt: str,
        custom_settings: Optional[dict] = None,
        tools: Sequence[Callable] = ()
    ) -> Agent[None, OutputT]:
        """
        Create an agent with STRICT PydanticAI v2 configuration.
        
        Args:
            provider_id: ID of the provider from providers.json
            output_type: Pydantic model for structured output
            system_prompt: System prompt for the agent
            custom_settings: Optional custom model settings (overrides defaults)
            tools: Sequence of tool functions to register with the agent
        
        Returns:
            Configured Agent instance
        
        Raises:
            ValueError: If provider not found or settings violate rules
        """
        registry = get_provider_registry()
        provider = registry.get_provider(provider_id)
        
        # Build model settings - start with defaults
        settings = provider.default_settings.copy()
        if custom_settings:
            settings.update(custom_settings)
        
        # STRICT validation for provider type
        registry.validate_settings(provider_id, settings)
        
        # Get API key from environment
        api_key = registry.get_api_key(provider_id)
        
        # Build model name for PydanticAI
        # Format: "provider:model"
        if provider.provider == "anthropic":
            model_name = f"anthropic:{provider.model}"
        elif provider.provider == "openai":
            model_name = f"openai:{provider.model}"
        else:
            raise ValueError(f"Unsupported provider: {provider.provider}")
        
        # Create agent with validated settings and tools
        # For reasoning models: model_settings contains ONLY reasoning_effort
        # For non-reasoning: model_settings contains ONLY temperature/top_p/max_tokens
        agent = Agent(
            model=model_name,
            output_type=output_type,
            system_prompt=system_prompt,
            model_settings=settings,
            tools=tools
        )
        
        return agent
    
    @staticmethod
    def validate_provider(provider_id: str) -> bool:
        """Check if provider exists and is properly configured"""
        try:
            registry = get_provider_registry()
            provider = registry.get_provider(provider_id)
            api_key = registry.get_api_key(provider_id)
            return True
        except (ValueError, FileNotFoundError):
            return False


def create_agent_for_session(
    session: dict,
    output_type: Type[OutputT],
    system_prompt: str,
    custom_settings: Optional[dict] = None,
    tools: Sequence[Callable] = ()
) -> Agent[None, OutputT]:
    """
    Create agent using provider from session state.
    
    Args:
        session: Session dict with 'active_provider_id' key
        output_type: Output type for agent
        system_prompt: System prompt
        custom_settings: Optional custom model settings
        tools: Sequence of tool functions to register with the agent
    
    Returns:
        Configured agent per PydanticAI v2 rules
    """
    provider_id = session.get("active_provider_id")
    
    if not provider_id:
        # Use default provider
        registry = get_provider_registry()
        provider_id = registry.default_provider_id
    
    return AgentFactory.create_agent(
        provider_id=provider_id,
        output_type=output_type,
        system_prompt=system_prompt,
        custom_settings=custom_settings,
        tools=tools
    )


def create_agent_for_task(
    task_type: str,
    output_type: Type[OutputT],
    system_prompt: str,
    custom_settings: Optional[dict] = None,
    tools: Sequence[Callable] = ()
) -> Agent[None, OutputT]:
    """
    Create agent using automatic routing based on task type.
    
    Args:
        task_type: Type of task (tags, bulk, reasoning, etc.)
        output_type: Output type for agent
        system_prompt: System prompt
        custom_settings: Optional custom model settings
        tools: Sequence of tool functions to register with the agent
    
    Returns:
        Configured agent routed to appropriate model
    """
    from .routing import ProviderRouter
    
    provider_id = ProviderRouter.route(task_type)
    
    return AgentFactory.create_agent(
        provider_id=provider_id,
        output_type=output_type,
        system_prompt=system_prompt,
        custom_settings=custom_settings,
        tools=tools
    )

