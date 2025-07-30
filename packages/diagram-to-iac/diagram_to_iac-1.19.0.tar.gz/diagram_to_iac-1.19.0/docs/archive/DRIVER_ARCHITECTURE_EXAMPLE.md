# LLM Driver Architecture - Design and Examples

## 🏗️ **Driver Architecture Overview**

The driver files in `llm_utils/` represent a **modular LLM provider abstraction layer** that would enhance the current router system with provider-specific optimizations and advanced features.

## 🎯 **What Each Driver Would Handle:**

### **1. Base Driver Interface (`base_driver.py`)**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel

class BaseLLMDriver(ABC):
    """Abstract base class for all LLM provider drivers."""
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate provider-specific configuration."""
        pass
    
    @abstractmethod
    def create_llm(self, config: Dict[str, Any]) -> BaseChatModel:
        """Create and configure LLM instance."""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Return list of supported models for this provider."""
        pass
    
    @abstractmethod
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        """Return capabilities for specific model (e.g., context length, function calling)."""
        pass
    
    @abstractmethod
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for given token usage."""
        pass
```

### **2. OpenAI Driver (`openai_driver.py`)**
```python
import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from .base_driver import BaseLLMDriver

class OpenAIDriver(BaseLLMDriver):
    """OpenAI-specific LLM driver with advanced features."""
    
    SUPPORTED_MODELS = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", 
        "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
    ]
    
    MODEL_CAPABILITIES = {
        "gpt-4o": {"context_length": 128000, "function_calling": True, "vision": True},
        "gpt-4o-mini": {"context_length": 128000, "function_calling": True, "vision": True},
        "gpt-4-turbo": {"context_length": 128000, "function_calling": True, "vision": True},
        "gpt-3.5-turbo": {"context_length": 16385, "function_calling": True, "vision": False},
    }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate OpenAI-specific configuration."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        model = config.get("model")
        if model and model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported OpenAI model: {model}")
        
        return True
    
    def create_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
        """Create optimized OpenAI LLM instance."""
        self.validate_config(config)
        
        # OpenAI-specific optimizations
        llm_config = {
            "model": config["model"],
            "temperature": config.get("temperature", 0.0),
            "max_tokens": config.get("max_tokens"),
            "top_p": config.get("top_p"),
            "frequency_penalty": config.get("frequency_penalty"),
            "presence_penalty": config.get("presence_penalty"),
        }
        
        # Remove None values
        llm_config = {k: v for k, v in llm_config.items() if v is not None}
        
        return ChatOpenAI(**llm_config)
    
    def get_supported_models(self) -> List[str]:
        return self.SUPPORTED_MODELS.copy()
    
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        return self.MODEL_CAPABILITIES.get(model, {})
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on OpenAI pricing (as of 2024)."""
        pricing = {
            "gpt-4o": {"input": 0.005, "output": 0.015},  # per 1K tokens
            "gpt-4o-mini": {"input": 0.000150, "output": 0.000600},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        }
        
        if model not in pricing:
            return 0.0
        
        rates = pricing[model]
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
```

### **3. Anthropic Driver (`anthropic_driver.py`)**
```python
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
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
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
        
        llm_config = {k: v for k, v in llm_config.items() if v is not None}
        return ChatAnthropic(**llm_config)
    
    def get_supported_models(self) -> List[str]:
        return self.SUPPORTED_MODELS.copy()
    
    def get_model_capabilities(self, model: str) -> Dict[str, Any]:
        # Claude-specific capabilities
        if "claude-3-5" in model:
            return {"context_length": 200000, "function_calling": True, "vision": True}
        elif "claude-3" in model:
            return {"context_length": 200000, "function_calling": True, "vision": "opus" in model}
        return {}
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        # Anthropic pricing logic
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        }
        
        if model not in pricing:
            return 0.0
        
        rates = pricing[model]
        return (input_tokens / 1000 * rates["input"]) + (output_tokens / 1000 * rates["output"])
```

### **4. Enhanced Router Integration**
```python
# Enhanced router.py with driver support
class LLMRouter:
    def __init__(self):
        self._drivers = {
            "openai": OpenAIDriver(),
            "anthropic": AnthropicDriver(),
            "google": GoogleDriver(),
        }
    
    def _create_llm_instance(self, config: Dict[str, Any]) -> BaseChatModel:
        """Create LLM using appropriate driver."""
        provider = config["provider"]
        driver = self._drivers.get(provider)
        
        if not driver:
            raise ValueError(f"No driver available for provider: {provider}")
        
        return driver.create_llm(config)
    
    def get_model_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get detailed model information including capabilities and cost estimation."""
        driver = self._drivers.get(provider)
        if not driver:
            return {}
        
        return {
            "capabilities": driver.get_model_capabilities(model),
            "supported": model in driver.get_supported_models(),
            "provider": provider
        }
    
    def estimate_conversation_cost(self, provider: str, model: str, conversation_history: List) -> float:
        """Estimate cost for entire conversation."""
        driver = self._drivers.get(provider)
        if not driver:
            return 0.0
        
        # Calculate token usage from conversation history
        input_tokens = sum(len(msg.content.split()) * 1.3 for msg in conversation_history)  # Rough estimation
        output_tokens = 150  # Estimated response length
        
        return driver.estimate_cost(model, int(input_tokens), output_tokens)
```

## 🌟 **Benefits of This Architecture:**

### **1. Separation of Concerns**
- Router handles configuration and orchestration
- Drivers handle provider-specific details
- Clean, maintainable code structure

### **2. Advanced Features**
- **Cost Estimation**: Know before you spend
- **Capability Detection**: Choose models based on features needed
- **Provider Optimization**: Each provider's unique strengths
- **Error Handling**: Provider-specific retry logic

### **3. Extensibility**
- Adding new providers is just adding a new driver
- Provider-specific features can be leveraged
- Easy A/B testing between providers

### **4. Enterprise Features**
- **Usage Tracking**: Per-provider usage analytics
- **Rate Limiting**: Provider-specific limits
- **Fallback Chains**: Automatic failover between providers
- **Caching**: Provider-optimized caching strategies

## 🚀 **Real-World Use Cases:**

### **1. Cost-Optimized Routing**
```python
# Automatically choose cheapest model for simple tasks
def get_cost_optimized_llm(task_complexity: str):
    if task_complexity == "simple":
        return router.get_llm_for_agent("budget_agent")  # Uses gpt-3.5-turbo
    elif task_complexity == "complex":
        return router.get_llm_for_agent("premium_agent")  # Uses gpt-4o
```

### **2. Capability-Based Selection**
```python
# Choose model based on required capabilities
def get_vision_capable_llm():
    for provider in ["openai", "anthropic", "google"]:
        for model in router.get_supported_models(provider):
            caps = router.get_model_capabilities(provider, model)
            if caps.get("vision"):
                return router.create_llm({"provider": provider, "model": model})
```

### **3. Multi-Provider Redundancy**
```python
# Fallback chain for high availability
async def robust_llm_call(prompt: str):
    providers = ["openai", "anthropic", "google"]
    for provider in providers:
        try:
            llm = router.get_llm_for_provider(provider)
            return await llm.ainvoke(prompt)
        except Exception as e:
            logger.warning(f"{provider} failed: {e}")
            continue
    raise Exception("All providers failed")
```

## 🎯 **Next Steps for Implementation:**

1. **Create Base Driver Interface** - Abstract class defining common methods
2. **Implement Provider Drivers** - One per LLM provider with specific optimizations
3. **Enhance Router Integration** - Use drivers in your existing router
4. **Add Advanced Features** - Cost estimation, capability detection, etc.
5. **Create Management Tools** - CLI tools for model comparison and selection

This architecture would make your LLM system incredibly powerful and enterprise-ready!
