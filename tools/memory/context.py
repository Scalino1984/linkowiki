# tools/memory/context.py
"""Session-overarching contextual memory for the LinkoWiki assistant"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from difflib import SequenceMatcher

BASE_DIR = Path(__file__).resolve().parents[2]
MEMORY_FILE = BASE_DIR / ".linkowiki-memory.json"


class ContextMemory:
    """Manages contextual memory across sessions"""
    
    def __init__(self):
        self.recent_actions: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        self.common_patterns: Dict[str, int] = {}
        self._load()
    
    def _load(self):
        """Load memory from disk"""
        if MEMORY_FILE.exists():
            try:
                data = json.loads(MEMORY_FILE.read_text(encoding='utf-8'))
                self.recent_actions = data.get('recent_actions', [])[-50:]  # Keep last 50
                self.user_preferences = data.get('user_preferences', {})
                self.common_patterns = data.get('common_patterns', {})
            except (json.JSONDecodeError, UnicodeDecodeError, IOError) as e:
                # If loading fails, start fresh
                pass
    
    def _save(self):
        """Save memory to disk"""
        try:
            data = {
                'recent_actions': self.recent_actions[-50:],  # Keep last 50
                'user_preferences': self.user_preferences,
                'common_patterns': self.common_patterns,
                'last_updated': datetime.now().isoformat()
            }
            MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
        except (json.JSONEncodeError, PermissionError, IOError) as e:
            pass  # Fail silently to not interrupt user workflow
    
    def remember_action(self, action: Dict[str, Any], prompt: str):
        """
        Remember an action with its associated prompt.
        
        Args:
            action: Action dictionary with type, path, content
            prompt: User prompt that led to this action
        """
        memory_entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'action': action
        }
        
        self.recent_actions.append(memory_entry)
        
        # Track common patterns
        pattern_key = f"{action.get('type', '')}:{action.get('path', '').split('/')[0]}"
        self.common_patterns[pattern_key] = self.common_patterns.get(pattern_key, 0) + 1
        
        self._save()
    
    def suggest_similar(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Suggest similar actions based on prompt history.
        
        Args:
            prompt: Current user prompt
            
        Returns:
            List of similar past actions with similarity scores
        """
        if not self.recent_actions:
            return []
        
        suggestions = []
        prompt_lower = prompt.lower()
        
        for entry in self.recent_actions[-20:]:  # Check last 20 actions
            past_prompt = entry['prompt'].lower()
            
            # Calculate similarity
            similarity = SequenceMatcher(None, prompt_lower, past_prompt).ratio()
            
            # Also check for keyword overlap
            prompt_words = set(prompt_lower.split())
            past_words = set(past_prompt.split())
            word_overlap = len(prompt_words & past_words) / max(len(prompt_words), 1)
            
            combined_score = (similarity * 0.6) + (word_overlap * 0.4)
            
            if combined_score > 0.3:  # Threshold for relevance
                suggestions.append({
                    'action': entry['action'],
                    'original_prompt': entry['prompt'],
                    'score': combined_score,
                    'timestamp': entry['timestamp']
                })
        
        # Sort by score and return top 3
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:3]
    
    def learn_preference(self, key: str, value: Any):
        """
        Learn and store a user preference.
        
        Args:
            key: Preference key (e.g., 'preferred_category', 'default_language')
            value: Preference value
        """
        self.user_preferences[key] = value
        self._save()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a stored preference.
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Stored preference value or default
        """
        return self.user_preferences.get(key, default)
    
    def get_common_patterns(self, limit: int = 5) -> List[tuple]:
        """
        Get most common action patterns.
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List of (pattern, count) tuples sorted by frequency
        """
        sorted_patterns = sorted(
            self.common_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_patterns[:limit]
    
    def detect_repeated_pattern(self, prompt: str) -> Optional[str]:
        """
        Detect if the current prompt matches a repeated pattern.
        
        Args:
            prompt: Current user prompt
            
        Returns:
            Hint text if pattern detected, None otherwise
        """
        # Check for phrases like "mach das gleiche für X"
        similar_phrases = [
            "mach das gleiche",
            "das gleiche für",
            "ähnlich wie",
            "wie bei",
            "do the same",
            "similar to"
        ]
        
        prompt_lower = prompt.lower()
        for phrase in similar_phrases:
            if phrase in prompt_lower:
                # Get last action for context
                if self.recent_actions:
                    last_action = self.recent_actions[-1]['action']
                    return f"Hinweis: Letzte Aktion war {last_action.get('type', '')} für {last_action.get('path', '')}"
        
        return None
    
    def clear(self):
        """Clear all memory (for testing or reset)"""
        self.recent_actions = []
        self.user_preferences = {}
        self.common_patterns = {}
        if MEMORY_FILE.exists():
            MEMORY_FILE.unlink()
