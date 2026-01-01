from pathlib import Path
from pydantic import BaseModel
from pydantic_ai import Agent
from tools.ai.agent_factory import create_agent_for_session
from tools.ai.agents.wiki_agent import get_wiki_system_prompt

WIKI_ROOT = Path("wiki")


class Action(BaseModel):
    type: str
    path: str
    content: str | None = None


class Option(BaseModel):
    """Interactive option for user selection"""
    label: str
    description: str | None = None


class AIResult(BaseModel):
    message: str
    options: list[Option] = []
    actions: list[Action] = []


def run_ai(prompt: str, files: dict, session: dict = None):
    """
    Run AI with current session's provider.
    Agent is created per request using session's active_provider_id.
    
    Args:
        prompt: User prompt
        files: Attached files dict
        session: Optional session dict (will load if not provided)
    
    Returns:
        AIResult with message, options, and actions
    """
    if session is None:
        from tools.session.manager import load_session
        session = load_session()
    
    # Ensure session has active_provider_id
    if not session or "active_provider_id" not in session or not session.get("active_provider_id"):
        from tools.ai.providers import get_provider_registry
        registry = get_provider_registry()
        if session:
            session["active_provider_id"] = registry.default_provider_id
        else:
            session = {"active_provider_id": registry.default_provider_id}
    
    # Build context
    context = ""
    if files:
        context += "ANGEHÄNGTE DATEIEN:\n"
        for name, content in files.items():
            context += f"\nDATEI {name}:\n{content}\n"
    
    full_prompt = f"{context}\nAUFGABE:\n{prompt}"
    
    # Create agent per request using session's provider
    agent = create_agent_for_session(
        session=session,
        output_type=AIResult,
        system_prompt=get_wiki_system_prompt()
    )
    
    result = agent.run_sync(full_prompt)
    return result.output


def run_ai_streaming(prompt: str, files: dict, session: dict = None):
    """
    Run AI with streaming output.
    
    Yields text chunks as they arrive.
    """
    if session is None:
        from tools.session.manager import load_session
        session = load_session()
    
    # Ensure session has active_provider_id
    if not session or "active_provider_id" not in session or not session.get("active_provider_id"):
        from tools.ai.providers import get_provider_registry
        registry = get_provider_registry()
        if session:
            session["active_provider_id"] = registry.default_provider_id
        else:
            session = {"active_provider_id": registry.default_provider_id}
    
    # Build context
    context = ""
    if files:
        context += "ANGEHÄNGTE DATEIEN:\n"
        for name, content in files.items():
            context += f"\nDATEI {name}:\n{content}\n"
    
    full_prompt = f"{context}\nAUFGABE:\n{prompt}"
    
    # Create agent per request using session's provider
    agent = create_agent_for_session(
        session=session,
        output_type=AIResult,
        system_prompt=get_wiki_system_prompt()
    )
    
    # Stream response
    for chunk in agent.run_stream(full_prompt):
        yield chunk


