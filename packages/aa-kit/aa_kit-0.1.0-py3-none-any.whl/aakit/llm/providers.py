"""
LLM Provider Implementations

Production-grade integrations with OpenAI and Anthropic APIs featuring
robust error handling, retries, and fallback mechanisms.
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator, Union
from dataclasses import dataclass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

import httpx

from ..core.exceptions import (
    LLMError, 
    RateLimitError, 
    ModelNotAvailableError,
    ConfigurationError
)


@dataclass
class LLMMessage:
    """Standardized message format across all providers."""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LLMResponse:
    """Standardized response format across all providers."""
    content: str
    model: str
    usage: Dict[str, int]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a chat completion."""
        pass
    
    @abstractmethod
    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Generate a streaming chat completion."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Check if a model is available."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider with comprehensive error handling."""
    
    AVAILABLE_MODELS = [
        "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview",
        "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
        "gpt-4o", "gpt-4o-mini"
    ]
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if None)
            base_url: Custom base URL for API calls
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationError(
                "OpenAI provider requires 'openai' package. Install with: pip install openai"
            )
        
        try:
            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize OpenAI client: {str(e)}")
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate OpenAI chat completion with retries."""
        if not self.validate_model(model):
            raise ModelNotAvailableError(model, self.AVAILABLE_MODELS)
        
        # Convert to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Retry logic for rate limits and transient errors
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=openai_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    metadata={
                        "finish_reason": response.choices[0].finish_reason,
                        "created": response.created
                    }
                )
                
            except openai.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise RateLimitError(
                        f"OpenAI rate limit exceeded: {str(e)}",
                        model=model,
                        retry_after=getattr(e, 'retry_after', None)
                    )
                
                # Exponential backoff
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                
            except openai.APIError as e:
                if attempt == max_retries - 1:
                    raise LLMError(
                        f"OpenAI API error: {str(e)}",
                        model=model,
                        error_code="API_ERROR"
                    )
                
                await asyncio.sleep(base_delay * (2 ** attempt))
                
            except Exception as e:
                raise LLMError(
                    f"Unexpected OpenAI error: {str(e)}",
                    model=model,
                    error_code="UNEXPECTED_ERROR"
                )
    
    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Generate streaming OpenAI chat completion."""
        if not self.validate_model(model):
            raise ModelNotAvailableError(model, self.AVAILABLE_MODELS)
        
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise LLMError(
                f"OpenAI streaming error: {str(e)}",
                model=model,
                error_code="STREAMING_ERROR"
            )
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return self.AVAILABLE_MODELS.copy()
    
    def validate_model(self, model: str) -> bool:
        """Check if OpenAI model is available."""
        return model in self.AVAILABLE_MODELS


class AnthropicProvider(LLMProvider):
    """Anthropic API provider with comprehensive error handling."""
    
    AVAILABLE_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229", 
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
    ]
    
    # Model aliases for convenience
    MODEL_ALIASES = {
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3-sonnet": "claude-3-sonnet-20240229",
        "claude-3-haiku": "claude-3-haiku-20240307",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "claude-3.5-haiku": "claude-3-5-haiku-20241022"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if None)
        """
        if not ANTHROPIC_AVAILABLE:
            raise ConfigurationError(
                "Anthropic provider requires 'anthropic' package. Install with: pip install anthropic"
            )
        
        try:
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Anthropic client: {str(e)}")
    
    def _resolve_model(self, model: str) -> str:
        """Resolve model aliases to full model names."""
        return self.MODEL_ALIASES.get(model, model)
    
    def _convert_messages(self, messages: List[LLMMessage]) -> tuple[str, List[Dict[str, str]]]:
        """Convert messages to Anthropic format (system + messages)."""
        system_message = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return system_message, anthropic_messages
    
    async def chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate Anthropic chat completion with retries."""
        resolved_model = self._resolve_model(model)
        
        if not self.validate_model(resolved_model):
            raise ModelNotAvailableError(
                resolved_model, 
                self.AVAILABLE_MODELS + list(self.MODEL_ALIASES.keys())
            )
        
        system_message, anthropic_messages = self._convert_messages(messages)
        
        # Default max_tokens for Anthropic
        if max_tokens is None:
            max_tokens = 4096
        
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                response = await self.client.messages.create(
                    model=resolved_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_message,
                    messages=anthropic_messages,
                    **kwargs
                )
                
                return LLMResponse(
                    content=response.content[0].text,
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                    },
                    metadata={
                        "stop_reason": response.stop_reason,
                        "stop_sequence": response.stop_sequence
                    }
                )
                
            except anthropic.RateLimitError as e:
                if attempt == max_retries - 1:
                    raise RateLimitError(
                        f"Anthropic rate limit exceeded: {str(e)}",
                        model=resolved_model
                    )
                
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
                
            except anthropic.APIError as e:
                if attempt == max_retries - 1:
                    raise LLMError(
                        f"Anthropic API error: {str(e)}",
                        model=resolved_model,
                        error_code="API_ERROR"
                    )
                
                await asyncio.sleep(base_delay * (2 ** attempt))
                
            except Exception as e:
                raise LLMError(
                    f"Unexpected Anthropic error: {str(e)}",
                    model=resolved_model,
                    error_code="UNEXPECTED_ERROR"
                )
    
    async def stream_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Generate streaming Anthropic chat completion."""
        resolved_model = self._resolve_model(model)
        
        if not self.validate_model(resolved_model):
            raise ModelNotAvailableError(
                resolved_model,
                self.AVAILABLE_MODELS + list(self.MODEL_ALIASES.keys())
            )
        
        system_message, anthropic_messages = self._convert_messages(messages)
        
        if max_tokens is None:
            max_tokens = 4096
        
        try:
            async with self.client.messages.stream(
                model=resolved_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=anthropic_messages,
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise LLMError(
                f"Anthropic streaming error: {str(e)}",
                model=resolved_model,
                error_code="STREAMING_ERROR"
            )
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models including aliases."""
        return self.AVAILABLE_MODELS.copy() + list(self.MODEL_ALIASES.keys())
    
    def validate_model(self, model: str) -> bool:
        """Check if Anthropic model is available."""
        resolved_model = self._resolve_model(model)
        return resolved_model in self.AVAILABLE_MODELS