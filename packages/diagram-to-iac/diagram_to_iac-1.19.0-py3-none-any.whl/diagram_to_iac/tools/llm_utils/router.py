import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from langchain_core.language_models.chat_models import BaseChatModel

# Import driver architecture
from .base_driver import BaseLLMDriver
from .openai_driver import OpenAIDriver
from .anthropic_driver import AnthropicDriver
from .gemini_driver import GoogleDriver
from .grok_driver import GrokDriver

# Import ConfigLoader for centralized configuration
from ...core.config_loader import ConfigLoader

try:
    from langchain_core.messages import HumanMessage
    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    LANGCHAIN_CORE_AVAILABLE = False

class LLMRouter:
    """
    Enhanced LLM Router that supports multiple providers and model policy configuration.
    Loads configuration from model_policy.yaml and routes to appropriate LLM providers.
    Uses driver architecture for provider-specific optimizations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the router with model policy configuration and drivers."""
        self.config = self._load_model_policy(config_path)
        self._provider_cache = {}
        
        # Initialize ConfigLoader for accessing centralized configuration
        self._config_loader = ConfigLoader()
        
        # Initialize drivers (including new Grok driver)
        self._drivers = {
            "openai": OpenAIDriver(),
            "anthropic": AnthropicDriver(),
            "google": GoogleDriver(),
            "grok": GrokDriver()
        }
    
    def _load_model_policy(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load model policy from YAML configuration."""
        if config_path is None:
            # Try multiple locations for model policy config
            possible_paths = [
                # Container workspace locations
                Path("/workspace/config/model_policy.yaml"),
                
                # Development environment
                Path.cwd() / "config" / "model_policy.yaml",
                
                # Package data locations (when installed via pip)
                Path(__file__).parent.parent.parent.parent / "config" / "model_policy.yaml",
                
                # Alternative package locations
                Path(__file__).resolve().parents[3] / "config" / "model_policy.yaml",
                Path(__file__).resolve().parents[4] / "config" / "model_policy.yaml",
                
                # Try relative to the workspace base from environment
                Path(os.environ.get("WORKSPACE_BASE", "/workspace")) / "config" / "model_policy.yaml",
            ]
            
            config_path = None
            for path in possible_paths:
                try:
                    if path.exists() and path.is_file():
                        config_path = path
                        break
                except (OSError, PermissionError):
                    # Skip paths that can't be accessed
                    continue
            
            # If still not found, try to find any model_policy.yaml file
            if not config_path:
                try:
                    # Search in common locations
                    for search_path in [Path("/workspace"), Path.cwd(), Path(__file__).parent.parent.parent.parent]:
                        for policy_file in search_path.rglob("model_policy.yaml"):
                            if policy_file.is_file():
                                config_path = policy_file
                                break
                        if config_path:
                            break
                except (OSError, PermissionError):
                    pass
            
            # Default fallback
            if not config_path:
                config_path = Path("/workspace/config/model_policy.yaml")
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                    print(f"✅ Model policy loaded from: {config_path}")
                    return config
            else:
                print(f"Warning: Model policy file not found at {config_path}. Using defaults.")
                return self._get_default_config()
        except FileNotFoundError:
            print(f"Warning: Model policy file not found at {config_path}. Using defaults.")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing model policy YAML: {e}. Using defaults.")
            return self._get_default_config()
        except Exception as e:
            print(f"Warning: Unexpected error loading model policy: {e}. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration when model_policy.yaml is not available."""
        return {
            "default": {
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "provider": "openai"
            },
            "models": {
                "gpt-4o-mini": {"provider": "openai", "api_key_env": "OPENAI_API_KEY"},
                "gpt-4o": {"provider": "openai", "api_key_env": "OPENAI_API_KEY"},
                "gpt-3.5-turbo": {"provider": "openai", "api_key_env": "OPENAI_API_KEY"}
            }
        }
    
    def _detect_provider(self, model_name: str) -> str:
        """Detect provider based on model name patterns."""
        model_lower = model_name.lower()
        
        if any(pattern in model_lower for pattern in ['gpt', 'openai']):
            return 'openai'
        elif any(pattern in model_lower for pattern in ['claude', 'anthropic']):
            return 'anthropic'
        elif any(pattern in model_lower for pattern in ['gemini', 'google']):
            return 'google'
        elif any(pattern in model_lower for pattern in ['grok', 'x.ai']):
            return 'grok'
        else:
            return 'openai'  # Default fallback
    
    def _check_api_key(self, provider: str) -> bool:
        """Check if required API key is available for the provider."""
        key_mapping = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'google': 'GOOGLE_API_KEY',
            'grok': 'GROK_API_KEY'
        }
        
        required_key = key_mapping.get(provider)
        if required_key and not os.getenv(required_key):
            return False
        return True
    
    def _get_available_providers(self) -> List[str]:
        """Get list of providers with available API keys."""
        available = []
        for provider in self._drivers.keys():
            if self._check_api_key(provider):
                available.append(provider)
        return available
    
    def _get_provider_selection_config(self) -> Dict[str, Any]:
        """Get provider selection configuration from centralized config."""
        try:
            app_config = self._config_loader.get_config()
            return app_config.get('ai', {}).get('provider_selection', {})
        except Exception:
            # Fallback to default behavior if config loading fails
            return {
                'strategy': 'auto',
                'preferred_order': ['openai', 'anthropic', 'google', 'grok'],
                'fallback': {'enabled': True, 'retry_attempts': 2}
            }
    
    def _select_best_provider(self, requested_provider: Optional[str] = None, 
                            requested_model: Optional[str] = None) -> tuple[str, str]:
        """
        Intelligently select the best available provider and model.
        
        Args:
            requested_provider: Explicitly requested provider (takes precedence)
            requested_model: Explicitly requested model (used for provider detection)
            
        Returns:
            tuple: (selected_provider, selected_model)
        """
        config = self._get_provider_selection_config()
        strategy = config.get('strategy', 'auto')
        
        # If provider explicitly requested, try that first
        if requested_provider and self._check_api_key(requested_provider):
            fallback_model = self._get_fallback_model_for_provider(requested_provider)
            return requested_provider, requested_model or fallback_model
        
        # If model specified, detect its provider and check availability
        if requested_model:
            detected_provider = self._detect_provider(requested_model)
            if self._check_api_key(detected_provider):
                return detected_provider, requested_model
        
        # Get available providers
        available_providers = self._get_available_providers()
        if not available_providers:
            raise ValueError(
                "No AI providers available. Please set at least one API key: "
                "OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, or GROK_API_KEY"
            )
        
        # Apply selection strategy
        if strategy == 'auto' or strategy == 'prefer_cost' or strategy == 'prefer_performance':
            preferred_order = config.get('preferred_order', ['openai', 'anthropic', 'google', 'grok'])
            
            # Filter to only available providers, maintaining preference order
            for provider in preferred_order:
                if provider in available_providers:
                    model = self._get_optimal_model_for_provider(provider, strategy, config)
                    return provider, model
        
        # Fallback to first available provider if strategy selection fails
        first_provider = available_providers[0]
        model = self._get_fallback_model_for_provider(first_provider)
        return first_provider, model
    
    def _get_optimal_model_for_provider(self, provider: str, strategy: str, config: Dict[str, Any]) -> str:
        """Get the optimal model for a provider based on selection strategy."""
        if strategy == 'prefer_cost':
            cost_models = config.get('cost_optimization', {}).get('prefer_models', [])
            for model in cost_models:
                if self._detect_provider(model) == provider:
                    return model
        elif strategy == 'prefer_performance':
            perf_models = config.get('performance_optimization', {}).get('prefer_models', [])
            for model in perf_models:
                if self._detect_provider(model) == provider:
                    return model
        
        # Fallback to provider's default model
        return self._get_fallback_model_for_provider(provider)
    
    def _get_fallback_model_for_provider(self, provider: str) -> str:
        """Get default/fallback model for a specific provider."""
        fallback_models = {
            'openai': 'gpt-4o-mini',
            'anthropic': 'claude-3-haiku',
            'google': 'gemini-pro',
            'grok': 'grok-1.5'
        }
        return fallback_models.get(provider, 'gpt-4o-mini')
    
    def get_llm_for_agent(self, agent_name: str) -> BaseChatModel:
        """
        Get an LLM instance configured for a specific agent with intelligent provider selection.
        Uses agent-specific configuration from model_policy.yaml and falls back to available providers.
        """
        config = self._resolve_model_config(agent_name)
        
        # Try intelligent provider selection with fallback
        try:
            # Check if configured provider is available
            if self._check_api_key(config['provider']):
                return self._create_llm_instance(config)
            else:
                # Provider not available, use intelligent selection
                print(f"Warning: Configured provider '{config['provider']}' not available for agent '{agent_name}'. Using intelligent fallback.")
                
                selected_provider, selected_model = self._select_best_provider(
                    requested_model=config.get('model')
                )
                
                # Update config with selected provider and model
                fallback_config = config.copy()
                fallback_config['provider'] = selected_provider
                fallback_config['model'] = selected_model
                
                return self._create_llm_instance(fallback_config)
                
        except Exception as e:
            # Last resort fallback
            available_providers = self._get_available_providers()
            if not available_providers:
                raise ValueError(
                    f"No AI providers available for agent '{agent_name}'. "
                    f"Please set at least one API key: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, or GROK_API_KEY"
                ) from e
            
            # Use first available provider with its default model
            fallback_provider = available_providers[0]
            fallback_model = self._get_fallback_model_for_provider(fallback_provider)
            
            fallback_config = config.copy()
            fallback_config['provider'] = fallback_provider
            fallback_config['model'] = fallback_model
            
            print(f"Warning: Fallback to {fallback_provider}/{fallback_model} for agent '{agent_name}' due to error: {e}")
            return self._create_llm_instance(fallback_config)
    
    def get_llm(self, model_name: str = None, temperature: float = None, agent_name: str = None) -> BaseChatModel:
        """
        Initializes and returns an LLM instance with intelligent provider selection.
        Uses provided parameters or falls back to agent-specific or global defaults.
        Automatically selects best available provider if configured provider is unavailable.
        """
        # If agent_name is provided but other params are None, use agent-specific config
        if agent_name and model_name is None and temperature is None:
            return self.get_llm_for_agent(agent_name)
        
        # Resolve model and temperature from policy configuration
        effective_model_name, effective_temperature = self._resolve_model_config_legacy(
            model_name, temperature, agent_name
        )
        
        # Use intelligent provider selection
        try:
            # Try to detect provider for the requested model
            initial_provider = self._detect_provider(effective_model_name)
            
            # Use intelligent selection to find best available option
            selected_provider, selected_model = self._select_best_provider(
                requested_provider=initial_provider if self._check_api_key(initial_provider) else None,
                requested_model=effective_model_name
            )
            
            # Create configuration dict
            config = {
                'model': selected_model,
                'temperature': effective_temperature,
                'provider': selected_provider
            }
            
            # Create and return the appropriate LLM instance
            return self._create_llm_instance(config)
            
        except Exception as e:
            # Last resort: use fallback configuration from policy
            print(f"Warning: Intelligent provider selection failed: {e}. Using fallback configuration.")
            
            fallback_config = self.config.get('default', {})
            fallback_provider = fallback_config.get('provider', 'openai')
            
            # If default provider is not available, try any available provider
            if not self._check_api_key(fallback_provider):
                available_providers = self._get_available_providers()
                if available_providers:
                    fallback_provider = available_providers[0]
                    effective_model_name = self._get_fallback_model_for_provider(fallback_provider)
                else:
                    raise ValueError(
                        "No AI providers available. Please set at least one API key: "
                        "OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, or GROK_API_KEY"
                    ) from e
            
            config = {
                'model': effective_model_name,
                'temperature': effective_temperature,
                'provider': fallback_provider
            }
            
            return self._create_llm_instance(config)
    
    def _resolve_model_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Resolve model configuration for a specific agent.
        Returns a dict with all config values, inheriting from defaults.
        """
        # Start with all default values
        default_config = self.config.get('default', {})
        config = default_config.copy()  # Copy all default values
        
        # Apply agent-specific configuration if available
        if agent_name:
            agent_config = self.config.get('agents', {}).get(agent_name, {})
            # Update config with any agent-specific overrides
            config.update(agent_config)
            
            # Auto-detect provider if not specified in either default or agent config
            if 'provider' not in config:
                config['provider'] = self._detect_provider(config.get('model', 'gpt-4o-mini'))
        
        return config
    
    def _resolve_model_config_legacy(self, model_name: str, temperature: float, agent_name: str) -> tuple[str, float]:
        """Resolve model name and temperature from configuration hierarchy (legacy method)."""
        # Start with defaults
        defaults = self.config.get('default', {})
        effective_model_name = defaults.get('model', 'gpt-4o-mini')
        effective_temperature = defaults.get('temperature', 0.0)
        
        # Apply agent-specific configuration if available
        if agent_name:
            agent_config = self.config.get('agents', {}).get(agent_name, {})
            if 'model' in agent_config:
                effective_model_name = agent_config['model']
            if 'temperature' in agent_config:
                effective_temperature = agent_config['temperature']
        
        # Override with explicit parameters
        if model_name is not None:
            effective_model_name = model_name
        if temperature is not None:
            effective_temperature = temperature
            
        return effective_model_name, effective_temperature
    
    def _create_llm_instance(self, config: Dict[str, Any]) -> BaseChatModel:
        """Create an LLM instance using the appropriate driver."""
        provider = config['provider']
        
        # Get the driver for this provider
        driver = self._drivers.get(provider)
        if not driver:
            raise ValueError(f"No driver available for provider: {provider}")
        
        # Use driver to create LLM instance
        return driver.create_llm(config)
    
    def get_supported_models(self, provider: str = None) -> Dict[str, List[str]]:
        """Get supported models for all providers or a specific provider."""
        if provider:
            driver = self._drivers.get(provider)
            if not driver:
                return {}
            return {provider: driver.get_supported_models()}
        
        # Return all supported models
        return {
            provider: driver.get_supported_models() 
            for provider, driver in self._drivers.items()
        }
    
    def get_model_capabilities(self, provider: str, model: str) -> Dict[str, Any]:
        """Get capabilities for a specific model."""
        driver = self._drivers.get(provider)
        if not driver:
            return {}
        return driver.get_model_capabilities(model)
    
    def estimate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a specific model and token usage."""
        driver = self._drivers.get(provider)
        if not driver:
            return 0.0
        return driver.estimate_cost(model, input_tokens, output_tokens)
    
    def get_all_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive information about all available models."""
        info = {}
        for provider, driver in self._drivers.items():
            info[provider] = {
                "available": self._check_api_key(provider),
                "models": driver.get_supported_models(),
                "capabilities": {
                    model: driver.get_model_capabilities(model)
                    for model in driver.get_supported_models()
                }
            }
        return info
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status information about all providers and intelligent selection."""
        available_providers = self._get_available_providers()
        config = self._get_provider_selection_config()
        
        return {
            "available_providers": available_providers,
            "total_providers": len(self._drivers),
            "selection_strategy": config.get('strategy', 'auto'),
            "preferred_order": config.get('preferred_order', []),
            "provider_details": {
                provider: {
                    "available": self._check_api_key(provider),
                    "api_key_env": f"{provider.upper()}_API_KEY",
                    "default_model": self._get_fallback_model_for_provider(provider)
                }
                for provider in self._drivers.keys()
            }
        }


# Create global router instance
_router_instance = None

def get_llm(model_name: str = None, temperature: float = None, agent_name: str = None) -> BaseChatModel:
    """
    Global function to get an LLM instance using the router.
    Provides backward compatibility with existing code.
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance.get_llm(model_name, temperature, agent_name)

# Example usage
if __name__ == '__main__':
    # Example usage (requires OPENAI_API_KEY to be set for default gpt-4o-mini)
    try:
        print("Testing enhanced LLM Router with model_policy.yaml support")
        print("=" * 60)
        
        print("\n1. Testing get_llm with no parameters (should use defaults):")
        llm_default = get_llm()
        print(f"  ✓ LLM Type: {type(llm_default).__name__}")
        print(f"  ✓ Model: {llm_default.model_name}")
        print(f"  ✓ Temperature: {llm_default.temperature}")

        print("\n2. Testing get_llm with specified parameters:")
        llm_custom = get_llm(model_name="gpt-3.5-turbo", temperature=0.5)
        print(f"  ✓ LLM Type: {type(llm_custom).__name__}")
        print(f"  ✓ Model: {llm_custom.model_name}")
        print(f"  ✓ Temperature: {llm_custom.temperature}")

        print("\n3. Testing agent-specific configuration:")
        llm_codegen = get_llm(agent_name="codegen_agent")
        print(f"  ✓ LLM Type: {type(llm_codegen).__name__}")
        print(f"  ✓ Model: {llm_codegen.model_name}")
        print(f"  ✓ Temperature: {llm_codegen.temperature}")
        
        print("\n4. Testing agent with overrides:")
        llm_question = get_llm(agent_name="question_agent")
        print(f"  ✓ LLM Type: {type(llm_question).__name__}")
        print(f"  ✓ Model: {llm_question.model_name}")
        print(f"  ✓ Temperature: {llm_question.temperature}")

        print("\n5. Testing fallback behavior with non-existent model:")
        llm_fallback = get_llm(model_name="non-existent-model")
        print(f"  ✓ LLM Type: {type(llm_fallback).__name__}")
        print(f"  ✓ Model: {llm_fallback.model_name}")
        print(f"  ✓ Temperature: {llm_fallback.temperature}")

        # Test actual LLM invocation if API key is available
        if os.getenv("OPENAI_API_KEY") and LANGCHAIN_CORE_AVAILABLE:
            print("\n6. Testing actual LLM invocation:")
            response = llm_default.invoke([HumanMessage(content="Hello! Respond with just 'Working!'")])
            print(f"  ✓ LLM Response: {response.content}")
        else:
            print("\n6. Skipping LLM invocation test (OPENAI_API_KEY not set or langchain_core not available)")

    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during get_llm tests: {e}")
