"""
Google Gemini LLM Driver

Provides Google Gemini-specific optimizations and features.
"""

import os
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from .base_driver import BaseLLMDriver


class GoogleDriver(BaseLLMDriver):
    """Google Gemini-specific LLM driver."""
    
    SUPPORTED_MODELS = [
        "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b",
        "gemini-1.0-pro", "gemini-pro", "gemini-pro-vision"
    ]
    
    MODEL_CAPABILITIES = {
        "gemini-1.5-pro": {"context_length": 1000000, "function_calling": True, "vision": True},
        "gemini-1.5-flash": {"context_length": 1000000, "function_calling": True, "vision": True},
        "gemini-1.5-flash-8b": {"context_length": 1000000, "function_calling": True, "vision": True},
        "gemini-1.0-pro": {"context_length": 30720, "function_calling": True, "vision": False},
        "gemini-pro": {"context_length": 30720, "function_calling": True, "vision": False},
        "gemini-pro-vision": {"context_length": 12288, "function_calling": False, "vision": True},
    }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Google-specific configuration."""
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        model = config.get("model")
        if model and model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported Google model: {model}. Supported models: {self.SUPPORTED_MODELS}")
        
        # Validate temperature range
        temperature = config.get("temperature")
        if temperature is not None and (temperature < 0 or temperature > 1):
            raise ValueError("Google temperature must be between 0 and 1")
        
        return True
    
    def create_llm(self, config: Dict[str, Any]) -> ChatGoogleGenerativeAI:
        """Create optimized Google LLM instance."""
        self.validate_config(config)
        
        # Google-specific optimizations
        llm_config = {
            "model": config["model"],
            "temperature": config.get("temperature", 0.0),
            "max_tokens": config.get("max_tokens"),
            "top_p": config.get("top_p"),
            "top_k": config.get("top_k"),  # Google-specific parameter
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
        }
        
        # Remove None values (except google_api_key)
        llm_config = {k: v for k, v in llm_config.items() if v is not None}
        
        return ChatGoogleGenerativeAI(**llm_config)
    
    def get_supported_models(self) -> List[str]:
        """Return list of supported Google models."""
        return self.SUPPORTED_MODELS.copy()
    
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """Return capabilities for specific Google model."""
        return self.MODEL_CAPABILITIES.get(model, {})
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on Google pricing (as of 2024)."""
        # Pricing per 1K tokens in USD
        pricing = {
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
            "gemini-1.5-flash-8b": {"input": 0.0000375, "output": 0.00015},
            "gemini-1.0-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-pro-vision": {"input": 0.00025, "output": 0.0005},
        }
        
        if model not in pricing:
            return 0.0
        
        rates = pricing[model]
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
