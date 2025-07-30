"""
Base LLM Driver Interface

This module provides the abstract base class for all LLM provider drivers.
Each driver implements provider-specific optimizations and features.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel


class BaseLLMDriver(ABC):
    """Abstract base class for all LLM provider drivers."""
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate provider-specific configuration.
        
        Args:
            config: Configuration dictionary containing model parameters
            
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def create_llm(self, config: Dict[str, Any]) -> BaseChatModel:
        """
        Create and configure LLM instance.
        
        Args:
            config: Configuration dictionary containing model parameters
            
        Returns:
            BaseChatModel: Configured LLM instance
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Return list of supported models for this provider.
        
        Returns:
            List[str]: List of supported model names
        """
        pass
    
    @abstractmethod
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """
        Return capabilities for specific model.
        
        Args:
            model: Model name
            
        Returns:
            Dict containing capabilities like context_length, function_calling, vision, etc.
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for given token usage.
        
        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            float: Estimated cost in USD
        """
        pass
    
    def get_provider_name(self) -> str:
        """
        Get the provider name for this driver.
        
        Returns:
            str: Provider name (e.g., 'openai', 'anthropic', 'google')
        """
        return self.__class__.__name__.lower().replace('driver', '')
