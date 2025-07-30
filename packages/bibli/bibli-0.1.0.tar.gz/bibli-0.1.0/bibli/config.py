"""Configuration management for Bible CLI."""

import os
import toml
from typing import Optional, Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for Bible CLI."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_dir = os.path.expanduser("~/.config/bible-cli")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.toml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return toml.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._get_default_config()
        else:
            # Create default config file
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "general": {
                "default_translation": "NIV",
                "theme": "dark",
                "page_size": 10,
                "show_verse_numbers": True,
            },
            "ascii_art": {
                "enabled": True,
                "style": "simple",
            },
            "mcp": {
                "enabled": False,
                "endpoint": "http://localhost:8000",
            },
            "cache": {
                "enabled": True,
                "directory": "~/.cache/bible-cli",
                "ttl_days": 30,
            },
            "keybindings": {
                "next_verse": ["j", "down"],
                "prev_verse": ["k", "up"],
                "search": ["/"],
                "quit": ["q", "ctrl+c"],
                "bookmark": ["m"],
                "random": ["r"],
                "goto": ["g"],
                "help": ["?"],
            },
            "database": {
                "path": "~/.local/share/bible-cli/bible.db",
            },
            "ui": {
                "border_style": "rounded",
                "highlight_color": "cyan",
                "text_color": "white",
                "background_color": "black",
            }
        }
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            toml.dump(config, f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def get_database_path(self) -> str:
        """Get database file path."""
        db_path = self.get("database.path", "~/.local/share/bible-cli/bible.db")
        expanded_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(expanded_path), exist_ok=True)
        return expanded_path
    
    def get_cache_directory(self) -> str:
        """Get cache directory path."""
        cache_dir = self.get("cache.directory", "~/.cache/bible-cli")
        expanded_path = os.path.expanduser(cache_dir)
        os.makedirs(expanded_path, exist_ok=True)
        return expanded_path
    
    def is_ascii_art_enabled(self) -> bool:
        """Check if ASCII art is enabled."""
        return self.get("ascii_art.enabled", True)
    
    def get_default_translation(self) -> str:
        """Get default Bible translation."""
        return self.get("general.default_translation", "NIV")
    
    def get_theme(self) -> str:
        """Get UI theme."""
        return self.get("general.theme", "dark")
    
    def get_page_size(self) -> int:
        """Get page size for pagination."""
        return self.get("general.page_size", 10)
    
    def show_verse_numbers(self) -> bool:
        """Check if verse numbers should be shown."""
        return self.get("general.show_verse_numbers", True)
    
    def get_keybinding(self, action: str) -> list:
        """Get keybinding for an action."""
        return self.get(f"keybindings.{action}", [])
    
    def get_ui_config(self) -> Dict[str, str]:
        """Get UI configuration."""
        return self.get("ui", {
            "border_style": "rounded",
            "highlight_color": "cyan",
            "text_color": "white",
            "background_color": "black",
        })
    
    def is_mcp_enabled(self) -> bool:
        """Check if MCP server is enabled."""
        return self.get("mcp.enabled", False)
    
    def get_mcp_endpoint(self) -> str:
        """Get MCP server endpoint."""
        return self.get("mcp.endpoint", "http://localhost:8000")
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.get("cache.enabled", True)
    
    def get_cache_ttl_days(self) -> int:
        """Get cache TTL in days."""
        return self.get("cache.ttl_days", 30)