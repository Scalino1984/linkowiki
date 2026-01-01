# tools/ai/tools/wiki_tools.py
"""Wiki-related tools for PydanticAI agent"""
from pathlib import Path
from typing import List, Dict, Any
import os

# Import wiki_search functions
import sys
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE_DIR))

from tools.wiki_search import search_wiki as wiki_search_func, list_recent_files

WIKI_ROOT = BASE_DIR / "wiki"


def search_wiki(query: str) -> List[Dict[str, Any]]:
    """
    Search the wiki for a specific term or phrase.
    
    Args:
        query: The search term or phrase to look for
        
    Returns:
        List of search results with file paths and matching lines
    """
    results = wiki_search_func(query, WIKI_ROOT)
    
    output = []
    for file_path, matches in results:
        relative_path = str(file_path.relative_to(WIKI_ROOT))
        output.append({
            "path": relative_path,
            "matches": matches[:5]  # Limit to 5 matches per file
        })
    
    return output[:10]  # Return max 10 files


def get_wiki_structure() -> Dict[str, Any]:
    """
    Get the current wiki directory structure.
    
    Returns:
        Dictionary representing the wiki structure with categories and entries
    """
    if not WIKI_ROOT.exists():
        return {"categories": [], "total_entries": 0}
    
    structure = {"categories": {}, "total_entries": 0}
    
    for item in WIKI_ROOT.rglob("*"):
        if item.is_file() and not item.name.startswith('.'):
            relative_path = item.relative_to(WIKI_ROOT)
            parts = relative_path.parts
            
            if len(parts) > 1:
                category = parts[0]
                if category not in structure["categories"]:
                    structure["categories"][category] = []
                structure["categories"][category].append(str(relative_path))
            else:
                if "root" not in structure["categories"]:
                    structure["categories"]["root"] = []
                structure["categories"]["root"].append(str(relative_path))
            
            structure["total_entries"] += 1
    
    return structure


def get_recent_changes(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recently modified wiki entries.
    
    Args:
        limit: Maximum number of entries to return (default: 10)
        
    Returns:
        List of recently modified files with their paths and modification times
    """
    recent_files = list_recent_files(WIKI_ROOT, limit=limit)
    
    output = []
    for file_path, mtime in recent_files:
        relative_path = str(file_path.relative_to(WIKI_ROOT))
        
        # Read first few lines for preview
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            preview = '\n'.join(lines[:3]) if len(lines) > 3 else content
        except:
            preview = ""
        
        from datetime import datetime
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        output.append({
            "path": relative_path,
            "modified": mod_time,
            "preview": preview
        })
    
    return output
