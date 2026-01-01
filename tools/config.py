# tools/config.py
"""Configuration management for LinkoWiki"""
import configparser
from pathlib import Path
from typing import Any, Optional


class Config:
    """Global configuration manager"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            # Create default config
            self._create_default_config()
        
        self.config.read(self.config_path)
    
    def _create_default_config(self):
        """Create default configuration file"""
        self.config['ai'] = {
            'default_provider': 'openai-gpt5-text',
            'default_temperature': '0.25',
            'default_reasoning_effort': 'medium'
        }
        self.config['session'] = {
            'max_history': '100',
            'auto_save': 'true',
            'default_mode': 'read'
        }
        self.config['wiki'] = {
            'wiki_root': 'wiki',
            'default_category': 'general',
            'max_file_size': '500'
        }
        self.config['ui'] = {
            'terminal_width': '0',
            'colors': 'true',
            'debug': 'false'
        }
        self.config['export'] = {
            'export_dir': 'session_exports',
            'export_format': 'markdown'
        }
        
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
    
    def save(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    # Convenience properties
    @property
    def default_provider(self) -> str:
        return self.get('ai', 'default_provider', 'openai-gpt5-text')
    
    @property
    def default_temperature(self) -> float:
        return self.getfloat('ai', 'default_temperature', 0.25)
    
    @property
    def default_reasoning_effort(self) -> str:
        return self.get('ai', 'default_reasoning_effort', 'medium')
    
    @property
    def default_session_mode(self) -> str:
        return self.get('session', 'default_mode', 'read')
    
    @property
    def wiki_root(self) -> Path:
        root = self.get('wiki', 'wiki_root', 'wiki')
        return Path(root)
    
    @property
    def export_dir(self) -> Path:
        export_dir = self.get('export', 'export_dir', 'session_exports')
        return Path(export_dir)
    
    @property
    def export_format(self) -> str:
        return self.get('export', 'export_format', 'markdown')
    
    @property
    def colors_enabled(self) -> bool:
        return self.getboolean('ui', 'colors', True)
    
    @property
    def debug_enabled(self) -> bool:
        return self.getboolean('ui', 'debug', False)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        base_dir = Path(__file__).resolve().parents[1]
        config_path = base_dir / "etc" / "linkowiki.conf"
        _config = Config(config_path)
    return _config


def reset_config():
    """Reset global config (for testing)"""
    global _config
    _config = None
