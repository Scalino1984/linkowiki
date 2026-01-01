# tools/ai/routing.py
"""Automatic provider routing based on task type"""
from typing import Literal

TaskType = Literal[
    "tags",
    "abstract",
    "metadata",
    "bulk",
    "rewrite",
    "summary",
    "structure",
    "outline",
    "analysis",
    "default"
]


class ProviderRouter:
    """Routes tasks to appropriate providers based on task characteristics"""
    
    # Routing rules as per specification
    ROUTING_MAP = {
        # Nano tasks - fast and cheap
        "tags": "openai-gpt5-nano-text",
        "abstract": "openai-gpt5-nano-text",
        "metadata": "openai-gpt5-nano-text",
        
        # Mini tasks - bulk operations
        "bulk": "openai-gpt5-mini-text",
        "rewrite": "openai-gpt5-mini-text",
        "summary": "openai-gpt5-mini-text",
        
        # Reasoning tasks - complex analysis
        "structure": "openai-gpt5-reasoning",
        "outline": "openai-gpt5-reasoning",
        "analysis": "openai-gpt5-reasoning",
        
        # Default - standard text model
        "default": "openai-gpt5-text"
    }
    
    @classmethod
    def route(cls, task_type: TaskType) -> str:
        """
        Route task to appropriate provider.
        
        Args:
            task_type: Type of task to perform
            
        Returns:
            Provider ID to use
        """
        return cls.ROUTING_MAP.get(task_type, cls.ROUTING_MAP["default"])
    
    @classmethod
    def detect_task_type(cls, prompt: str) -> TaskType:
        """
        Auto-detect task type from prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            Detected task type
        """
        prompt_lower = prompt.lower()
        
        # Nano detection (tags, metadata, simple extraction)
        if any(kw in prompt_lower for kw in ["tag", "tags", "tagging", "schlagwort"]):
            return "tags"
        if any(kw in prompt_lower for kw in ["abstract", "zusammenfassung", "kurz"]):
            return "abstract"
        if any(kw in prompt_lower for kw in ["metadata", "metadaten", "eigenschaft"]):
            return "metadata"
        
        # Mini detection (bulk, rewrite, summary)
        if any(kw in prompt_lower for kw in ["bulk", "masse", "viele", "alle"]):
            return "bulk"
        if any(kw in prompt_lower for kw in ["rewrite", "umschreiben", "überarbeiten"]):
            return "rewrite"
        if any(kw in prompt_lower for kw in ["summarize", "summary", "zusammenfassen"]):
            return "summary"
        
        # Reasoning detection (structure, outline, analysis)
        if any(kw in prompt_lower for kw in ["structure", "struktur", "organisieren"]):
            return "structure"
        if any(kw in prompt_lower for kw in ["outline", "gliederung", "übersicht"]):
            return "outline"
        if any(kw in prompt_lower for kw in ["analyze", "analysis", "analysiere"]):
            return "analysis"
        
        # Default
        return "default"
    
    @classmethod
    def route_auto(cls, prompt: str) -> str:
        """
        Automatically detect task type and route.
        
        Args:
            prompt: User prompt
            
        Returns:
            Provider ID to use
        """
        task_type = cls.detect_task_type(prompt)
        return cls.route(task_type)
