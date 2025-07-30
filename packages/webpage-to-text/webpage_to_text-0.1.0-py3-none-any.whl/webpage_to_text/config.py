"""
Configuration management for webpage-to-text.
"""

import json
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path


class Config:
    """Configuration handler for webpage-to-text."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = Path(config_path) if config_path else None
        self.config = {}
        
        if self.config_path and self.config_path.exists():
            self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                self.config = yaml.safe_load(f)
            elif self.config_path.suffix.lower() == '.json':
                self.config = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {self.config_path.suffix}")
        
        return self.config
    
    def save_config(self, output_path: str) -> None:
        """Save configuration to file."""
        output_path = Path(output_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if output_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            elif output_path.suffix.lower() == '.json':
                json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {output_path.suffix}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def get_urls(self) -> List[str]:
        """Get list of URLs from configuration."""
        return self.config.get("urls", [])
    
    def get_output_dir(self) -> str:
        """Get output directory from configuration."""
        return self.config.get("output_dir", "./extracted_texts")
    
    def get_rate_limit(self) -> float:
        """Get rate limit from configuration."""
        return self.config.get("rate_limit", 1.0)
    
    def get_filenames(self) -> Optional[List[str]]:
        """Get custom filenames from configuration."""
        return self.config.get("filenames", None)
    
    @classmethod
    def create_sample_config(cls, output_path: str) -> None:
        """Create a sample configuration file."""
        sample_config = {
            "name": "Sample Website Extraction",
            "description": "Extract content from sample websites",
            "output_dir": "./extracted_texts",
            "rate_limit": 1.0,
            "urls": [
                "https://example.com",
                "https://example.com/about",
                "https://example.com/contact"
            ],
            "filenames": [
                "001_home.txt",
                "002_about.txt", 
                "003_contact.txt"
            ]
        }
        
        config = cls()
        config.config = sample_config
        config.save_config(output_path)