"""
Anthropic LLM Driver

Provides Anthropic Claude-specific optimizations and features.
"""

import os
from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from .base_driver import BaseLLMDriver


class AnthropicDriver(BaseLLMDriver):
    """Anthropic Claude-specific LLM driver."""
    
    SUPPORTED_MODELS = [
        "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
        "claude-3-haiku-20240307"
    ]
    
    MODEL_CAPABILITIES = {
        "claude-3-5-sonnet-20241022": {"context_length": 200000, "function_calling": True, "vision": True},
        "claude-3-5-haiku-20241022": {"context_length": 200000, "function_calling": True, "vision": True},
        "claude-3-opus-20240229": {"context_length": 200000, "function_calling": True, "vision": True},
        "claude-3-sonnet-20240229": {"context_length": 200000, "function_calling": True, "vision": True},
        "claude-3-haiku-20240307": {"context_length": 200000, "function_calling": True, "vision": False},
    }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Anthropic-specific configuration."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        model = config.get("model")
        if model and model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported Anthropic model: {model}. Supported models: {self.SUPPORTED_MODELS}")
        
        # Validate temperature range
        temperature = config.get("temperature")
        if temperature is not None and (temperature < 0 or temperature > 1):
            raise ValueError("Anthropic temperature must be between 0 and 1")
        
        return True
    
    def create_llm(self, config: Dict[str, Any]) -> ChatAnthropic:
        """Create optimized Anthropic LLM instance."""
        self.validate_config(config)
        
        # Anthropic-specific optimizations
        llm_config = {
            "model": config["model"],
            "temperature": config.get("temperature", 0.0),
            "max_tokens": config.get("max_tokens", 1024),
            "top_p": config.get("top_p"),
            "top_k": config.get("top_k"),  # Anthropic-specific parameter
        }
        
        # Remove None values
        llm_config = {k: v for k, v in llm_config.items() if v is not None}
        
        return ChatAnthropic(**llm_config)
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported Anthropic models."""
        return self.SUPPORTED_MODELS.copy()
    
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """Return capabilities for specific Anthropic model."""
        return self.MODEL_CAPABILITIES.get(model, {})
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on Anthropic pricing (as of 2024)."""
        # Pricing per 1K tokens in USD
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-5-haiku-20241022": {"input": 0.00025, "output": 0.00125},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        }
        
        if model not in pricing:
            return 0.0
        
        rates = pricing[model]
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
