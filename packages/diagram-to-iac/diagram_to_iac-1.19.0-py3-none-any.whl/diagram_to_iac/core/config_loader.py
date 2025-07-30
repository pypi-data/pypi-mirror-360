# src/diagram_to_iac/core/config_loader.py
"""
Central configuration loader for diagram-to-iac project.
Handles loading and merging configuration from multiple sources with environment variable overrides.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import lru_cache

logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Central configuration management for the diagram-to-iac project.
    Loads configuration from central config.yaml file with environment variable override capability.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigLoader with optional custom config path.
        
        Args:
            config_path: Path to central config file (default: src/diagram_to_iac/config.yaml)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set default paths (container-safe)
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Try multiple locations for central config
            possible_paths = [
                Path.cwd() / "src" / "diagram_to_iac" / "config.yaml",  # Development
                Path(__file__).parent.parent / "config.yaml",  # Package location
                Path("/workspace/src/diagram_to_iac/config.yaml"),  # Container workspace
                Path("/workspace/config.yaml"),  # Container root
            ]
            self.config_path = None
            for path in possible_paths:
                if path.exists():
                    self.config_path = path
                    break
            # Default to package location if none found (will create defaults)
            if not self.config_path:
                self.config_path = Path(__file__).parent.parent / "config.yaml"
        
        # Cache for loaded config
        self._config = None
    
    @lru_cache(maxsize=1)
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete configuration with environment variable overrides.
        
        Returns:
            Configuration dictionary
        """
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from central config file.
        
        Returns:
            Configuration dictionary with environment overrides applied
        """
        # Load base config
        config = self._load_config_file()
        
        # Apply environment variable overrides
        config = self._apply_env_overrides(config)
        
        self.logger.debug("Configuration loaded successfully")
        return config
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from central YAML file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                self.logger.debug(f"Loaded config from {self.config_path}")
            else:
                self.logger.warning(f"Config file not found at {self.config_path}, using built-in defaults")
                config = self._get_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            config = self._get_default_config()
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config file is not available."""
        return {
            'system': {
                'workspace_base': '/workspace',
                'log_level': 'INFO'
            },
            'network': {
                'api_timeout': 10,
                'shell_timeout': 30,
                'terraform_timeout': 300,
                'github_timeout': 15,
                'git_timeout': 300
            },
            'ai': {
                'default_model': 'gpt-4o-mini',
                'default_temperature': 0.1,
                'max_tokens': 1000
            }
        }
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.
        Environment variables should be in the format: DIAGRAM_TO_IAC_<SECTION>_<KEY>
        Also supports some common direct environment variables like COPILOT_ASSIGNEE.
        
        Args:
            config: Base configuration dictionary
            
        Returns:
            Configuration with environment overrides applied
        """
        result = config.copy()
        env_prefix = "DIAGRAM_TO_IAC_"
        
        # Get list of allowed overrides from config
        allowed_overrides = config.get("environment_overrides", {}).get("allowed_overrides", [])
        
        # Handle special direct environment variables
        special_env_mappings = {
            "COPILOT_ASSIGNEE": "github.copilot_assignee",
            "WORKSPACE_BASE": "system.workspace_base",
            "LOG_LEVEL": "system.log_level"
        }
        
        # Process special environment variables first
        for env_var, config_path in special_env_mappings.items():
            if env_var in os.environ and config_path in allowed_overrides:
                converted_value = self._convert_env_value(os.environ[env_var])
                self._set_nested_value(result, config_path, converted_value)
                self.logger.debug(f"Applied special environment override: {config_path} = {converted_value}")
        
        # Process standard DIAGRAM_TO_IAC_ prefixed variables
        for env_var, env_value in os.environ.items():
            if not env_var.startswith(env_prefix):
                continue
                
            # Parse environment variable name
            # e.g., DIAGRAM_TO_IAC_NETWORK_API_TIMEOUT -> network.api_timeout
            var_path = env_var[len(env_prefix):].lower().replace('_', '.')
            
            # Check if override is allowed
            if var_path not in allowed_overrides:
                self.logger.debug(f"Environment override not allowed: {var_path}")
                continue
            
            # Convert string value to appropriate type
            converted_value = self._convert_env_value(env_value)
            
            # Apply override to config
            self._set_nested_value(result, var_path, converted_value)
            self.logger.debug(f"Applied environment override: {var_path} = {converted_value}")
        
        return result
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """
        Convert environment variable string value to appropriate type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a nested value in configuration using dot notation.
        
        Args:
            config: Configuration dictionary to modify
            path: Dot-separated path (e.g., "network.api_timeout")
            value: Value to set
        """
        keys = path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a specific configuration section.
        
        Args:
            section: Section name (e.g., "network", "ai", "routing")
            
        Returns:
            Configuration section dictionary
        """
        return self.get_config().get(section, {})
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "network.api_timeout")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = self.get_config()
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def reload(self) -> None:
        """Reload configuration from file (clears cache)."""
        self._config = None
        self.get_config.cache_clear()
        self.logger.debug("Configuration cache cleared, will reload on next access")


# Global configuration loader instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def get_config() -> Dict[str, Any]:
    """Get the complete merged configuration."""
    return get_config_loader().get_config()

def get_config_section(section: str) -> Dict[str, Any]:
    """Get a specific configuration section."""
    return get_config_loader().get_section(section)

def get_config_value(path: str, default: Any = None) -> Any:
    """Get a configuration value using dot notation."""
    return get_config_loader().get_value(path, default)

def reload_config() -> None:
    """Reload configuration from files."""
    get_config_loader().reload()
