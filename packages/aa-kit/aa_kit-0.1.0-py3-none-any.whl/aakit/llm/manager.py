"""
LLM Manager - Unified interface for all LLM providers

Handles provider selection, fallbacks, model management, and provides
a clean abstraction layer for the reasoning engine.
"""

import os
import asyncio
from typing import Dict, List, Optional, AsyncIterator, Any, Union
from dataclasses import dataclass

from .providers import LLMProvider, OpenAIProvider, AnthropicProvider, LLMMessage, LLMResponse
from ..core.exceptions import LLMError, ModelNotAvailableError, ConfigurationError


@dataclass
class LLMConfig:
    """Configuration for LLM Manager."""
    primary_model: str
    fallback_models: List[str]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 60
    max_retries: int = 3


class LLMManager:
    """
    Unified LLM management with automatic provider detection and fallbacks.
    
    Features:
    - Automatic provider detection based on model names
    - Intelligent fallbacks when primary models fail
    - Environment variable auto-detection
    - Comprehensive error handling
    - Streaming support
    """
    
    # Model to provider mapping
    MODEL_PROVIDERS = {
        # OpenAI models
        "gpt-4": "openai",
        "gpt-4-turbo": "openai", 
        "gpt-4-turbo-preview": "openai",
        "gpt-3.5-turbo": "openai",
        "gpt-3.5-turbo-16k": "openai",
        "gpt-4o": "openai",
        "gpt-4o-mini": "openai",
        
        # Anthropic models
        "claude-3-opus": "anthropic",
        "claude-3-sonnet": "anthropic",
        "claude-3-haiku": "anthropic", 
        "claude-3.5-sonnet": "anthropic",
        "claude-3.5-haiku": "anthropic",
        "claude-3-opus-20240229": "anthropic",
        "claude-3-sonnet-20240229": "anthropic",
        "claude-3-haiku-20240307": "anthropic",
        "claude-3-5-sonnet-20241022": "anthropic",
        "claude-3-5-haiku-20241022": "anthropic",
    }
    
    def __init__(
        self,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        fallback_models: Optional[List[str]] = None,
        timeout: int = 60,
        max_retries: int = 3,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None
    ):
        """
        Initialize LLM Manager.
        
        Args:
            model: Primary model to use
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            fallback_models: Models to try if primary fails
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            openai_api_key: OpenAI API key (uses OPENAI_API_KEY env var if None)
            anthropic_api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if None)
            openai_base_url: Custom OpenAI base URL
        """
        self.config = LLMConfig(
            primary_model=model,
            fallback_models=fallback_models or self._get_default_fallbacks(model),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Initialize providers
        self.providers: Dict[str, LLMProvider] = {}
        
        # Auto-detect API keys from environment
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        anthropic_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize OpenAI provider if key is available
        if openai_key:
            try:
                self.providers["openai"] = OpenAIProvider(
                    api_key=openai_key,
                    base_url=openai_base_url
                )
            except Exception:
                # Don't fail initialization, just skip this provider
                pass
        
        # Initialize Anthropic provider if key is available
        if anthropic_key:
            try:
                self.providers["anthropic"] = AnthropicProvider(api_key=anthropic_key)
            except Exception:
                # Don't fail initialization, just skip this provider
                pass
        
        # Validate primary model is supported
        if not self._can_handle_model(self.config.primary_model):
            # Check if it's a known model even if provider isn't available
            if self.config.primary_model not in self.MODEL_PROVIDERS:
                available_models = self.get_available_models()
                raise ModelNotAvailableError(
                    self.config.primary_model,
                    available_models
                )
            # If it's a known model but provider isn't available, we'll fail at runtime
            # This allows agent creation without API keys for testing
    
    def _get_default_fallbacks(self, primary_model: str) -> List[str]:
        """Get intelligent fallback models based on primary model."""
        if primary_model.startswith("gpt-4"):
            return ["gpt-3.5-turbo", "claude-3-haiku"]
        elif primary_model.startswith("gpt-3.5"):
            return ["gpt-4", "claude-3-haiku"]
        elif "claude-3-opus" in primary_model:
            return ["claude-3-sonnet", "gpt-4"]
        elif "claude-3-sonnet" in primary_model or "claude-3.5-sonnet" in primary_model:
            return ["claude-3-haiku", "gpt-4"]
        elif "claude-3-haiku" in primary_model or "claude-3.5-haiku" in primary_model:
            return ["claude-3-sonnet", "gpt-3.5-turbo"]
        else:
            return ["gpt-4", "claude-3-haiku"]
    
    def _get_provider_for_model(self, model: str) -> Optional[str]:
        """Get the provider name for a given model."""
        return self.MODEL_PROVIDERS.get(model)
    
    def _can_handle_model(self, model: str) -> bool:
        """Check if we can handle a specific model."""
        provider_name = self._get_provider_for_model(model)
        if not provider_name:
            return False
        
        provider = self.providers.get(provider_name)
        if not provider:
            return False
        
        return provider.validate_model(model)
    
    def get_available_models(self) -> List[str]:
        """Get all available models across all providers."""
        available_models = []
        
        for provider in self.providers.values():
            available_models.extend(provider.get_available_models())
        
        return list(set(available_models))  # Remove duplicates
    
    async def chat(
        self,
        messages: Union[str, List[LLMMessage]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """
        Generate a chat completion with automatic fallbacks.
        
        Args:
            messages: Either a string message or list of LLMMessage objects
            model: Model to use (defaults to primary model)
            temperature: Temperature override
            max_tokens: Max tokens override
            **kwargs: Additional parameters for the provider
            
        Returns:
            LLMResponse with the generated content
        """
        # Convert string message to LLMMessage list
        if isinstance(messages, str):
            messages = [LLMMessage(role="user", content=messages)]
        
        # Use provided parameters or fall back to config
        target_model = model or self.config.primary_model
        target_temperature = temperature if temperature is not None else self.config.temperature
        target_max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        # Try primary model first, then fallbacks
        models_to_try = [target_model] + self.config.fallback_models
        
        last_error = None
        
        for attempt_model in models_to_try:
            if not self._can_handle_model(attempt_model):
                continue
            
            provider_name = self._get_provider_for_model(attempt_model)
            provider = self.providers[provider_name]
            
            try:
                response = await provider.chat(
                    messages=messages,
                    model=attempt_model,
                    temperature=target_temperature,
                    max_tokens=target_max_tokens,
                    **kwargs
                )
                
                # Add fallback information to metadata
                if attempt_model != target_model:
                    response.metadata["fallback_used"] = True
                    response.metadata["requested_model"] = target_model
                    response.metadata["actual_model"] = attempt_model
                
                return response
                
            except Exception as e:
                last_error = e
                # Continue to next fallback model
                continue
        
        # If all models failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise LLMError(
                f"No available providers for any of the models: {models_to_try}",
                error_code="NO_AVAILABLE_PROVIDERS"
            )
    
    async def stream_chat(
        self,
        messages: Union[str, List[LLMMessage]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion.
        
        Args:
            messages: Either a string message or list of LLMMessage objects
            model: Model to use (defaults to primary model)
            temperature: Temperature override  
            max_tokens: Max tokens override
            **kwargs: Additional parameters for the provider
            
        Yields:
            Partial response chunks as they become available
        """
        # Convert string message to LLMMessage list
        if isinstance(messages, str):
            messages = [LLMMessage(role="user", content=messages)]
        
        target_model = model or self.config.primary_model
        target_temperature = temperature if temperature is not None else self.config.temperature
        target_max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        # For streaming, only try the requested model (no fallbacks)
        if not self._can_handle_model(target_model):
            raise ModelNotAvailableError(target_model, self.get_available_models())
        
        provider_name = self._get_provider_for_model(target_model)
        provider = self.providers[provider_name]
        
        async for chunk in provider.stream_chat(
            messages=messages,
            model=target_model,
            temperature=target_temperature,
            max_tokens=target_max_tokens,
            **kwargs
        ):
            yield chunk
    
    def add_provider(self, name: str, provider: LLMProvider) -> None:
        """
        Add a custom provider.
        
        Args:
            name: Provider name
            provider: LLMProvider instance
        """
        self.providers[name] = provider
    
    def remove_provider(self, name: str) -> None:
        """
        Remove a provider.
        
        Args:
            name: Provider name to remove
        """
        if name in self.providers:
            del self.providers[name]
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about available providers and models.
        
        Returns:
            Dictionary with provider information
        """
        info = {
            "providers": {},
            "primary_model": self.config.primary_model,
            "fallback_models": self.config.fallback_models,
            "total_models": len(self.get_available_models())
        }
        
        for name, provider in self.providers.items():
            info["providers"][name] = {
                "available_models": provider.get_available_models(),
                "model_count": len(provider.get_available_models())
            }
        
        return info