"""Anthropic provider adapter for DeepSentinel.

This module implements the Anthropic provider adapter, supporting Claude models
with comprehensive functionality including chat completions, streaming support,
robust error handling, and middleware integration.
"""

import asyncio
import json
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional

from aiohttp import ClientResponseError, ClientSession

from ..config import ProviderConfig
from ..exceptions import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from ..types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    Message,
    MessageRole,
    StreamChunk,
    Usage,
)
from .base import BaseLLMProvider

# Configure logging
logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider adapter for DeepSentinel.

    This adapter provides comprehensive Anthropic Claude API support with:
    - Chat completions with streaming support
    - Text completion emulation via chat completions
    - Robust error handling with exponential backoff
    - Compliance middleware integration
    - Performance monitoring and logging
    - Support for all Claude models
    
    Attributes:
        config: Provider configuration
        name: Provider name
        provider_type: Type of the provider (anthropic)
    """
    
    # Anthropic model constraints and defaults
    MAX_TOKENS_BY_MODEL = {
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
        "claude-2.1": 200000,
        "claude-2.0": 100000,
        "claude-instant-1.2": 100000,
        "claude-instant-1": 100000,
    }
    
    # Default max tokens for models if not specified
    DEFAULT_MAX_TOKENS = 1024
    
    def __init__(self, config: ProviderConfig, name: str) -> None:
        """Initialize the Anthropic provider adapter.
        
        Args:
            config: Provider configuration
            name: Name identifier for this provider instance
        """
        super().__init__(config, name)
        self._session: Optional[ClientSession] = None
        self._semaphore = asyncio.Semaphore(
            self.config.extra_config.get("connection_limit", 10)
        )
        
        # API version control
        self._api_version = self.config.extra_config.get(
            "api_version", "2023-06-01"
        )
        
        # Request tracking for performance monitoring
        self._request_count = 0
        self._total_tokens = 0
        self._last_reset_time = time.time()
        
        # Rate limiting tracking (Anthropic specific headers)
        self._rate_limit_requests = 0
        self._rate_limit_tokens = 0
        self._rate_limit_reset_requests = 0
        self._rate_limit_reset_tokens = 0
        
        logger.info(
            f"Initialized Anthropic provider '{name}' with config: "
            f"timeout={config.timeout}s, max_retries={config.max_retries}, "
            f"api_version={self._api_version}"
        )
    
    async def initialize(self) -> None:
        """Initialize the Anthropic client and connection.
        
        This method sets up the aiohttp session for API calls, validates
        configuration, and performs initial connectivity tests.
        
        Raises:
            ProviderError: If initialization fails or API key is missing
            AuthenticationError: If API key is invalid
        """
        try:
            if not self.config.api_key:
                raise AuthenticationError(
                    "Anthropic API key is required for authentication",
                    provider_name=self.name,
                )
            
            # Initialize HTTP session if needed
            if self._session is None or self._session.closed:
                self._session = await self._get_http_session()
            
            # Perform initial health check to validate configuration
            try:
                await self.health_check()
                logger.info(
                    f"Anthropic provider '{self.name}' initialized "
                    f"successfully"
                )
            except Exception as e:
                logger.warning(
                    f"Health check failed during initialization for "
                    f"provider '{self.name}': {e}"
                )
                # Don't fail initialization on health check failure
            
            self._initialized = True
            
        except AuthenticationError:
            raise
        except Exception as e:
            error_msg = f"Failed to initialize Anthropic provider: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ProviderError(
                error_msg,
                provider_name=self.name,
                provider_error=e,
            ) from e
    
    async def _cleanup_provider_resources(self) -> None:
        """Clean up Anthropic provider-specific resources.
        
        Closes the aiohttp session and logs final statistics.
        """
        if self._session and not self._session.closed:
            await self._session.close()
        
        # Log final statistics
        logger.info(
            f"Anthropic provider '{self.name}' cleanup: "
            f"requests={self._request_count}, "
            f"total_tokens={self._total_tokens}"
        )
        
        self._initialized = False
    
    def _get_default_base_url(self) -> str:
        """Get the default base URL for the Anthropic API.
        
        Returns:
            Default Anthropic API base URL
        """
        return "https://api.anthropic.com/v1"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check on the Anthropic provider.
        
        Tests API connectivity, authentication, and basic functionality.
        
        Returns:
            Dictionary containing detailed health status information
            
        Raises:
            ProviderError: If health check fails
        """
        start_time = time.time()
        health_status = {
            "status": "unknown",
            "provider": self.provider_type.value,
            "timestamp": int(time.time()),
            "response_time_ms": 0,
            "api_available": False,
            "models_available": 0,
            "rate_limits": {},
        }
        
        try:
            # Test basic connectivity with a minimal request
            test_request = ChatRequest(
                messages=[
                    Message(role=MessageRole.USER, content="Hi")
                ],
                # Use fastest model for health check
                model="claude-3-haiku-20240307",
                max_tokens=1,
            )
            
            # Prepare the request but don't complete it (to save costs)
            payload = self._prepare_chat_payload(test_request)
            headers = self._prepare_headers()
            url = self._build_request_url("/messages")
            
            # Make a HEAD request or minimal request to test connectivity
            async with self._session.post(
                url,
                headers=headers,
                json=payload,
                timeout=5,
            ) as response:
                status = response.status
                # Extract rate limit information if available
                self._extract_rate_limit_headers(response.headers)
                
                # Even if the request fails due to minimal tokens,
                # a 400 error indicates the API is reachable and auth works
                # Only 5xx errors indicate API issues
                api_available = status < 500
            
            # Get available models
            models = await self.list_models()
            
            health_status.update({
                "status": "healthy" if api_available else "unhealthy",
                "api_available": api_available,
                "models_available": len(models),
                "response_time_ms": int((time.time() - start_time) * 1000),
                "rate_limits": {
                    "requests_remaining": getattr(
                        self, '_rate_limit_requests', 0
                    ),
                    "tokens_remaining": getattr(self, '_rate_limit_tokens', 0),
                    "reset_requests": getattr(
                        self, '_rate_limit_reset_requests', 0
                    ),
                    "reset_tokens": getattr(
                        self, '_rate_limit_reset_tokens', 0
                    ),
                },
            })
            
            logger.debug(
                f"Health check passed for Anthropic provider '{self.name}'"
            )
            return health_status
            
        except AuthenticationError as e:
            health_status.update({
                "status": "unhealthy",
                "error": "Authentication failed",
                "error_type": "authentication",
                "response_time_ms": int((time.time() - start_time) * 1000),
            })
            logger.error(
                f"Authentication failed for Anthropic provider "
                f"'{self.name}': {e}"
            )
            return health_status
            
        except Exception as e:
            health_status.update({
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time_ms": int((time.time() - start_time) * 1000),
            })
            logger.error(
                f"Health check failed for Anthropic provider "
                f"'{self.name}': {e}"
            )
            return health_status
    
    async def chat_completion(
        self, request: ChatRequest, **kwargs: Any
    ) -> ChatResponse:
        """Create a chat completion using Anthropic API.
        
        Supports all Anthropic Claude models with comprehensive
        error handling, validation, and performance monitoring.
        
        Args:
            request: Chat completion request
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            Chat completion response
            
        Raises:
            ProviderError: If the operation fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limits are exceeded
            ValidationError: If request validation fails
        """
        start_time = time.time()
        
        try:
            # Validate request structure
            self.validate_request(request)
            self._validate_chat_request(request)
            
            # Prepare the request payload
            payload = self._prepare_chat_payload(request, **kwargs)
            payload["stream"] = False
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making chat completion request to Anthropic: "
                f"model={request.model}, messages={len(request.messages)}"
            )
            
            # Make the API request with retry logic
            async with self._semaphore:
                response_data = await self._make_api_request(
                    "post",
                    "/messages",
                    json=payload,
                )
            
            # Update tracking metrics
            self._update_metrics(response_data, start_time)
            
            # Convert Anthropic response to standard ChatResponse
            response = self._convert_anthropic_response(
                response_data, request.model
            )
            
            logger.debug(
                f"Chat completion successful: "
                f"tokens="
                f"{response.usage.total_tokens if response.usage else 0}"
            )
            
            return response
        
        except Exception as e:
            # Log error with context
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Chat completion failed after {duration_ms}ms: {str(e)}",
                exc_info=True
            )
            self.handle_provider_error(e, "chat_completion")
            # This line should not be reached but keeps type checker happy
            raise ProviderError("Failed to create chat completion")
    
    async def chat_completion_stream(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming chat completion using Anthropic API.
        
        Provides real-time streaming of chat completion responses with
        proper error handling and chunk validation.
        
        Args:
            request: Chat completion request
            **kwargs: Additional Anthropic-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limits are exceeded
            ValidationError: If request validation fails
        """
        start_time = time.time()
        chunk_count = 0
        
        try:
            # Validate request structure
            self.validate_request(request)
            self._validate_chat_request(request)
            
            # Prepare the request payload
            payload = self._prepare_chat_payload(request, **kwargs)
            payload["stream"] = True
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making streaming chat completion request to Anthropic: "
                f"model={request.model}, messages={len(request.messages)}"
            )
            
            # Make the streaming API request
            async with self._semaphore:
                async for chunk_data in self._make_streaming_request(
                    "/messages",
                    json=payload,
                ):
                    chunk_count += 1
                    try:
                        # Convert Anthropic chunk to standard format
                        chunk = self._convert_anthropic_stream_chunk(
                            chunk_data, request.model
                        )
                        if chunk:
                            yield chunk
                    except Exception as chunk_error:
                        logger.warning(
                            f"Failed to parse stream chunk {chunk_count}: "
                            f"{chunk_error}"
                        )
                        continue
            
            # Log streaming completion
            duration_ms = int((time.time() - start_time) * 1000)
            logger.debug(
                f"Streaming chat completion finished: "
                f"chunks={chunk_count}, duration={duration_ms}ms"
            )
        
        except Exception as e:
            # Log error with context
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Streaming chat completion failed after {duration_ms}ms: "
                f"{str(e)}",
                exc_info=True
            )
            self.handle_provider_error(e, "chat_completion_stream")
    
    async def text_completion(
        self, request: CompletionRequest, **kwargs: Any
    ) -> CompletionResponse:
        """Create a text completion using Anthropic API.
        
        Note: Anthropic doesn't support traditional text completions,
        so this method emulates it by using chat completions with a user
        message.
        
        Args:
            request: Text completion request
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            Text completion response
            
        Raises:
            ProviderError: If the operation fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limits are exceeded
            ValidationError: If request validation fails
        """
        start_time = time.time()
        
        try:
            # Validate request structure
            self.validate_request(request)
            self._validate_completion_request(request)
            
            # Convert text completion request to chat completion
            chat_request = self._convert_completion_to_chat_request(request)
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making text completion request to Anthropic: "
                f"model={request.model}, prompt_length="
                f"{len(str(request.prompt)) if request.prompt else 0}"
            )
            
            # Use the chat_completion method
            chat_response = await self.chat_completion(chat_request, **kwargs)
            
            # Convert chat response to text completion response format
            response = self._convert_chat_to_completion_response(
                chat_response, request
            )
            
            logger.debug(
                f"Text completion successful: "
                f"tokens="
                f"{response.usage.total_tokens if response.usage else 0}"
            )
            
            return response
        
        except Exception as e:
            # Log error with context
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Text completion failed after {duration_ms}ms: {str(e)}",
                exc_info=True
            )
            self.handle_provider_error(e, "text_completion")
            # This line should not be reached but keeps type checker happy
            raise ProviderError("Failed to create text completion")
    
    async def text_completion_stream(
        self, request: CompletionRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming text completion using Anthropic API.
        
        Note: Anthropic doesn't support traditional text completions,
        so this method emulates it by using chat completions with a user
        message.
        
        Args:
            request: Text completion request
            **kwargs: Additional Anthropic-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limits are exceeded
            ValidationError: If request validation fails
        """
        start_time = time.time()
        chunk_count = 0
        
        try:
            # Validate request structure
            self.validate_request(request)
            self._validate_completion_request(request)
            
            # Convert text completion request to chat completion
            chat_request = self._convert_completion_to_chat_request(
                request, stream=True
            )
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making streaming text completion request to Anthropic: "
                f"model={request.model}, prompt_length="
                f"{len(str(request.prompt)) if request.prompt else 0}"
            )
            
            # Use the chat_completion_stream method but convert chunks
            async for chunk in self.chat_completion_stream(
                chat_request, **kwargs
            ):
                chunk_count += 1
                # Convert chat stream format to text completion stream format
                converted_chunk = self._convert_chat_to_completion_stream_chunk(
                    chunk
                )
                if converted_chunk:
                    yield converted_chunk
            
            # Log streaming completion
            duration_ms = int((time.time() - start_time) * 1000)
            logger.debug(
                f"Streaming text completion finished: "
                f"chunks={chunk_count}, duration={duration_ms}ms"
            )
        
        except Exception as e:
            # Log error with context
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Streaming text completion failed after {duration_ms}ms: "
                f"{str(e)}",
                exc_info=True
            )
            self.handle_provider_error(e, "text_completion_stream")
    
    async def create_embeddings(
        self, request: EmbeddingRequest, **kwargs: Any
    ) -> EmbeddingResponse:
        """Create embeddings for input text.
        
        Note: Anthropic doesn't currently support embeddings.
        This method raises a ProviderError.
        
        Args:
            request: Embedding request
            **kwargs: Additional parameters
            
        Raises:
            ProviderError: Always, as Anthropic doesn't support embeddings
        """
        raise ProviderError(
            "Embeddings are not supported by the Anthropic provider. "
            "Consider using OpenAI or another provider for embedding "
            "generation.",
            provider_name=self.name,
        )
    
    async def list_models(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List available Anthropic models.
        
        Note: Anthropic doesn't have a models listing API.
        This method returns a static list of known Claude models.
        
        Args:
            **kwargs: Additional parameters (unused)
            
        Returns:
            List of available models with metadata
        """
        # Anthropic doesn't have a models listing API, so we return a static list
        models = [
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "created": 1709251200,  # March 1, 2024
                "description": "Most powerful Claude model for highly complex tasks",
                "context_window": 200000,
                "max_output": 4096,
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet", 
                "created": 1709251200,  # March 1, 2024
                "description": "Balanced Claude model for enterprise workloads",
                "context_window": 200000,
                "max_output": 4096,
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "created": 1709769600,  # March 7, 2024
                "description": "Fastest and most compact Claude model",
                "context_window": 200000,
                "max_output": 4096,
            },
            {
                "id": "claude-2.1",
                "name": "Claude 2.1",
                "created": 1699574400,  # November 9, 2023
                "description": "Previous generation Claude model with improved accuracy",
                "context_window": 200000,
                "max_output": 4096,
            },
            {
                "id": "claude-2.0",
                "name": "Claude 2",
                "created": 1689120000,  # July 11, 2023
                "description": "Previous generation Claude model",
                "context_window": 100000,
                "max_output": 4096,
            },
            {
                "id": "claude-instant-1.2",
                "name": "Claude Instant 1.2",
                "created": 1679616000,  # March 24, 2023
                "description": "Fast, affordable Claude model for lighter tasks",
                "context_window": 100000,
                "max_output": 4096,
            },
        ]
        
        logger.debug(f"Listed {len(models)} Anthropic models")
        return models
    
    async def get_model(
        self, model_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get information about a specific model.
        
        Note: Anthropic doesn't have a model information API.
        This method returns static information for known models
        or raises an error for unknown models.
        
        Args:
            model_id: ID of the model to retrieve
            **kwargs: Additional parameters (unused)
            
        Returns:
            Model information and metadata
            
        Raises:
            ProviderError: If the model is not known
        """
        # Get the list of models and find the requested one
        models = await self.list_models()
        for model in models:
            if model["id"] == model_id:
                logger.debug(f"Retrieved model info for {model_id}")
                return model
        
        raise ProviderError(
            f"Unknown Anthropic model: {model_id}. "
            f"Available models: {', '.join(m['id'] for m in models)}",
            provider_name=self.name,
        )
    
    def _validate_chat_request(self, request: ChatRequest) -> None:
        """Validate chat completion request parameters.
        
        Args:
            request: Chat completion request to validate
            
        Raises:
            ValidationError: If request parameters are invalid
        """
        # Check model constraints
        if request.model in self.MAX_TOKENS_BY_MODEL:
            max_tokens = self.MAX_TOKENS_BY_MODEL[request.model]
            if request.max_tokens and request.max_tokens > max_tokens:
                raise ValidationError(
                    f"max_tokens ({request.max_tokens}) exceeds limit "
                    f"for model {request.model} ({max_tokens})",
                    field_name="max_tokens",
                    field_value=request.max_tokens,
                )
        
        # Validate messages structure
        if not request.messages:
            raise ValidationError(
                "At least one message is required",
                field_name="messages",
                field_value=request.messages,
            )
        
        # Check for proper conversation structure
        has_user_message = any(
            msg.role == MessageRole.USER for msg in request.messages
        )
        if not has_user_message:
            raise ValidationError(
                "At least one user message is required",
                field_name="messages",
                field_value=[msg.role.value for msg in request.messages],
            )
        
        # Validate max_tokens is provided (required by Anthropic)
        if not request.max_tokens:
            # Set default if not provided
            request.max_tokens = self.DEFAULT_MAX_TOKENS
    
    def _validate_completion_request(self, request: CompletionRequest) -> None:
        """Validate text completion request parameters.
        
        Args:
            request: Text completion request to validate
            
        Raises:
            ValidationError: If request parameters are invalid
        """
        # Validate prompt
        if not request.prompt:
            raise ValidationError(
                "Prompt is required for text completion",
                field_name="prompt",
                field_value=request.prompt,
            )
        
        # Check model constraints
        if request.model in self.MAX_TOKENS_BY_MODEL:
            max_tokens = self.MAX_TOKENS_BY_MODEL[request.model]
            if request.max_tokens and request.max_tokens > max_tokens:
                raise ValidationError(
                    f"max_tokens ({request.max_tokens}) exceeds limit "
                    f"for model {request.model} ({max_tokens})",
                    field_name="max_tokens",
                    field_value=request.max_tokens,
                )
        
        # Ensure max_tokens is set
        if not request.max_tokens:
            request.max_tokens = self.DEFAULT_MAX_TOKENS
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for Anthropic API requests.
        
        Returns:
            Dictionary of headers to include in requests
        """
        headers = {
            "User-Agent": f"DeepSentinel-SDK/0.1.0 ({self.provider_type.value})",
            "Content-Type": "application/json",
            **self.config.headers,
        }
        
        # Anthropic uses x-api-key header instead of Authorization
        if self.config.api_key:
            headers["x-api-key"] = self.config.api_key
        
        # Add Anthropic-specific headers
        headers["anthropic-version"] = self._api_version
        
        return headers
    
    def _prepare_chat_payload(
        self, request: ChatRequest, **kwargs: Any
    ) -> Dict[str, Any]:
        """Convert our standard chat request to Anthropic API format.
        
        Args:
            request: Standard chat request
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            Dictionary in Anthropic API format
        """
        # Start with the parameters we can directly map
        payload = {
            "model": request.model,
            "max_tokens": request.max_tokens or self.DEFAULT_MAX_TOKENS,
        }
        
        # Add optional parameters if provided
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.stop is not None:
            payload["stop_sequences"] = (
                [request.stop] if isinstance(request.stop, str) else request.stop
            )
        if request.user is not None:
            payload["metadata"] = {"user_id": request.user}
        
        # Process messages - Anthropic has specific requirements
        system_prompt = None
        messages = []
        
        # Extract system prompt and convert message format
        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
            elif msg.role in (MessageRole.USER, MessageRole.ASSISTANT):
                messages.append({
                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                    "content": msg.content or "",
                })
            # Note: Anthropic doesn't support function/tool messages in the same way
            # We could potentially convert these to user messages with special formatting
        
        # Add system prompt if present
        if system_prompt:
            payload["system"] = system_prompt
        
        # Add messages
        payload["messages"] = messages
        
        # Add tool/function calling if present (Anthropic format)
        if request.tools:
            payload["tools"] = self._convert_tools_to_anthropic_format(request.tools)
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice
        
        # Add any additional kwargs as parameters
        for key, value in kwargs.items():
            if value is not None and key not in payload:
                payload[key] = value
        
        return payload
    
    def _convert_tools_to_anthropic_format(
        self, tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert OpenAI-style tools to Anthropic format.
        
        Args:
            tools: Tools in OpenAI format
            
        Returns:
            Tools in Anthropic format
        """
        # Anthropic has a different tool format than OpenAI
        # This is a basic conversion - might need refinement
        anthropic_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                anthropic_tools.append({
                    "name": func.get("name"),
                    "description": func.get("description"),
                    "input_schema": func.get("parameters", {}),
                })
        return anthropic_tools
    
    def _convert_completion_to_chat_request(
        self, request: CompletionRequest, stream: bool = False
    ) -> ChatRequest:
        """Convert text completion request to chat completion request.
        
        Args:
            request: Text completion request
            stream: Whether this is for streaming
            
        Returns:
            Equivalent chat completion request
        """
        # Convert prompt to user message
        content = (
            request.prompt 
            if isinstance(request.prompt, str)
            else "\n".join(request.prompt)
        )
        
        return ChatRequest(
            messages=[Message(role=MessageRole.USER, content=content)],
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop=request.stop,
            stream=stream,
            user=request.user,
        )
    
    def _convert_anthropic_response(
        self, response: Dict[str, Any], model: str
    ) -> ChatResponse:
        """Convert Anthropic response to standard ChatResponse format.
        
        Args:
            response: Anthropic API response
            model: Model ID used for the request
            
        Returns:
            Standardized ChatResponse object
        """
        # Extract the message content from Anthropic's format
        message_content = response.get("content", [])
        text_content = ""
        
        # Process the content blocks (Anthropic returns content as blocks)
        for block in message_content:
            if block.get("type") == "text":
                text_content += block.get("text", "")
        
        # Create usage information
        usage_data = response.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=(
                usage_data.get("input_tokens", 0) + 
                usage_data.get("output_tokens", 0)
            ),
        ) if usage_data else None
        
        # Create a standard ChatResponse
        return ChatResponse(
            id=response.get("id", ""),
            object="chat.completion",
            created=int(time.time()),  # Anthropic doesn't provide created timestamp
            model=model,
            choices=[
                {
                    "index": 0,
                    "message": Message(
                        role=MessageRole.ASSISTANT,
                        content=text_content,
                    ),
                    "finish_reason": self._convert_stop_reason(
                        response.get("stop_reason", "stop")
                    ),
                }
            ],
            usage=usage,
        )
    
    def _convert_anthropic_stream_chunk(
        self, chunk: Dict[str, Any], model: str
    ) -> Optional[StreamChunk]:
        """Convert Anthropic streaming chunk to standard StreamChunk format.
        
        Args:
            chunk: Anthropic API streaming chunk
            model: Model ID used for the request
            
        Returns:
            Standardized StreamChunk object or None for non-content chunks
        """
        chunk_type = chunk.get("type")
        
        # Handle different types of streaming events from Anthropic
        if chunk_type == "content_block_delta":
            # This contains the actual text content
            delta_data = chunk.get("delta", {})
            text = delta_data.get("text", "")
            
            return StreamChunk(
                id=chunk.get("message", {}).get("id", ""),
                object="chat.completion.chunk",
                created=int(time.time()),
                model=model,
                choices=[
                    {
                        "index": 0,
                        "delta": {
                            "role": MessageRole.ASSISTANT,
                            "content": text,
                        },
                        "finish_reason": None,
                    }
                ],
            )
        
        elif chunk_type == "message_stop":
            # This indicates the end of the stream
            return StreamChunk(
                id=chunk.get("message", {}).get("id", ""),
                object="chat.completion.chunk",
                created=int(time.time()),
                model=model,
                choices=[
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": self._convert_stop_reason(
                            chunk.get("stop_reason", "stop")
                        ),
                    }
                ],
            )
        
        # Skip other chunk types (message_start, content_block_start, etc.)
        return None
    
    def _convert_chat_to_completion_response(
        self, chat_response: ChatResponse, original_request: CompletionRequest
    ) -> CompletionResponse:
        """Convert chat response to text completion response format.
        
        Args:
            chat_response: Chat completion response
            original_request: Original completion request
            
        Returns:
            Text completion response
        """
        choices = []
        for idx, choice in enumerate(chat_response.choices):
            text = choice.message.content or ""
            choices.append({
                "text": text,
                "index": idx,
                "finish_reason": choice.finish_reason,
                "logprobs": choice.get("logprobs"),
            })
        
        return CompletionResponse(
            id=chat_response.id,
            object="text_completion",
            created=chat_response.created,
            model=chat_response.model,
            choices=choices,
            usage=chat_response.usage,
        )
    
    def _convert_chat_to_completion_stream_chunk(
        self, chunk: StreamChunk
    ) -> Optional[StreamChunk]:
        """Convert chat streaming chunk to text completion format.
        
        Args:
            chunk: Chat completion streaming chunk
            
        Returns:
            Converted text completion streaming chunk or None
        """
        if not chunk.choices:
            return None
        
        # Extract content from the delta
        choices = []
        for choice in chunk.choices:
            delta = choice.get("delta", {})
            content = delta.get("content", "")
            
            choices.append({
                "index": choice.get("index", 0),
                "text": content,
                "finish_reason": choice.get("finish_reason"),
                "logprobs": choice.get("logprobs"),
            })
        
        # Create a text completion chunk format
        return StreamChunk(
            id=chunk.id,
            object="text_completion.chunk",
            created=chunk.created,
            model=chunk.model,
            choices=choices,
            usage=chunk.usage,
        )
    
    def _convert_stop_reason(self, anthropic_stop_reason: str) -> str:
        """Convert Anthropic stop reason to standard format.
        
        Args:
            anthropic_stop_reason: Anthropic's stop reason
            
        Returns:
            Standard stop reason
        """
        # Map Anthropic stop reasons to standard OpenAI-compatible reasons
        reason_mapping = {
            "end_turn": "stop",
            "max_tokens": "length",
            "stop_sequence": "stop",
            "tool_use": "tool_calls",
        }
        return reason_mapping.get(anthropic_stop_reason, "stop")
    
    def _update_metrics(
        self, response_data: Dict[str, Any], start_time: float
    ) -> None:
        """Update performance metrics from API response.
        
        Args:
            response_data: API response data
            start_time: Request start time
        """
        self._request_count += 1
        
        # Update token usage if available
        if "usage" in response_data:
            usage = response_data["usage"]
            total_tokens = (
                usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            )
            self._total_tokens += total_tokens
        
        # Record performance metrics
        duration = time.time() - start_time
        self._record_request_metrics(duration, 0, success=True)
    
    def _extract_rate_limit_headers(self, headers: Any) -> None:
        """Extract rate limit information from response headers.
        
        Args:
            headers: Response headers
        """
        # Extract Anthropic rate limit headers if they exist
        # Note: Anthropic may use different header names than OpenAI
        self._rate_limit_requests = int(
            headers.get("anthropic-ratelimit-requests-remaining", 0)
        )
        self._rate_limit_tokens = int(
            headers.get("anthropic-ratelimit-tokens-remaining", 0)
        )
        
        # Extract reset times if available
        if "anthropic-ratelimit-requests-reset" in headers:
            self._rate_limit_reset_requests = int(
                headers["anthropic-ratelimit-requests-reset"]
            )
        if "anthropic-ratelimit-tokens-reset" in headers:
            self._rate_limit_reset_tokens = int(
                headers["anthropic-ratelimit-tokens-reset"]
            )
    
    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the Anthropic API with comprehensive error handling.
        
        Args:
            method: HTTP method (get, post, etc.)
            endpoint: API endpoint path
            **kwargs: Additional parameters for the request
            
        Returns:
            Parsed JSON response
            
        Raises:
            ProviderError: If the request fails after retries
            AuthenticationError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        if not self.is_initialized:
            await self.initialize()
        
        url = self._build_request_url(endpoint)
        headers = self._prepare_headers()
        
        # Use the retry mechanism from the base class
        async def request_func():
            async with getattr(self._session, method)(
                url,
                headers=headers,
                timeout=self._request_timeout,
                **kwargs,
            ) as response:
                # Extract rate limit information
                self._extract_rate_limit_headers(response.headers)
                
                if response.status >= 400:
                    error_text = await response.text()
                    
                    # Parse error response
                    try:
                        error_json = json.loads(error_text)
                        error_data = error_json.get("error", {})
                        error_message = error_data.get("message", error_text)
                        error_type = error_data.get("type", "unknown")
                    except json.JSONDecodeError:
                        error_message = error_text
                        error_type = "unknown"
                    
                    # Handle specific error types
                    if response.status == 401:
                        raise AuthenticationError(
                            f"Anthropic authentication failed: {error_message}",
                            provider_name=self.name,
                            details={"type": error_type},
                        )
                    elif response.status == 429:
                        retry_after = None
                        if "retry-after" in response.headers:
                            try:
                                retry_after = int(response.headers["retry-after"])
                            except ValueError:
                                pass
                        
                        raise RateLimitError(
                            f"Anthropic rate limit exceeded: {error_message}",
                            provider_name=self.name,
                            retry_after=retry_after,
                            details={
                                "type": error_type,
                                "requests_remaining": self._rate_limit_requests,
                                "tokens_remaining": self._rate_limit_tokens,
                            },
                        )
                    else:
                        raise ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Anthropic API error: {error_message}",
                            headers=response.headers,
                        )
                
                return await response.json()
        
        return await self._make_request_with_retry(request_func)
    
    async def _make_streaming_request(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Make a streaming request to the Anthropic API with error handling.
        
        Args:
            endpoint: API endpoint path
            **kwargs: Additional parameters for the request
            
        Yields:
            Parsed JSON chunks from the streaming response
            
        Raises:
            ProviderError: If the request fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limits are exceeded
        """
        if not self.is_initialized:
            await self.initialize()
        
        url = self._build_request_url(endpoint)
        headers = self._prepare_headers()
        
        try:
            async with self._session.post(
                url,
                headers=headers,
                timeout=self._request_timeout,
                **kwargs,
            ) as response:
                # Extract rate limit information
                self._extract_rate_limit_headers(response.headers)
                
                if response.status >= 400:
                    error_text = await response.text()
                    
                    # Parse error response
                    try:
                        error_json = json.loads(error_text)
                        error_data = error_json.get("error", {})
                        error_message = error_data.get("message", error_text)
                        error_type = error_data.get("type", "unknown")
                    except json.JSONDecodeError:
                        error_message = error_text
                        error_type = "unknown"
                    
                    # Handle specific error types
                    if response.status == 401:
                        raise AuthenticationError(
                            f"Anthropic authentication failed: {error_message}",
                            provider_name=self.name,
                            details={"type": error_type},
                        )
                    elif response.status == 429:
                        retry_after = None
                        if "retry-after" in response.headers:
                            try:
                                retry_after = int(response.headers["retry-after"])
                            except ValueError:
                                pass
                        
                        raise RateLimitError(
                            f"Anthropic rate limit exceeded: {error_message}",
                            provider_name=self.name,
                            retry_after=retry_after,
                            details={
                                "type": error_type,
                                "requests_remaining": self._rate_limit_requests,
                                "tokens_remaining": self._rate_limit_tokens,
                            },
                        )
                    else:
                        raise ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Anthropic API error: {error_message}",
                            headers=response.headers,
                        )
                
                # Process the streaming response
                async for line in response.content:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Anthropic uses event-stream format similar to OpenAI
                    if line.startswith(b"data: "):
                        try:
                            # Remove "data: " prefix
                            json_str = line[6:].decode("utf-8")
                            
                            # Skip [DONE] messages
                            if json_str.strip() == "[DONE]":
                                continue
                            
                            chunk = json.loads(json_str)
                            yield chunk
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # Skip malformed chunks but continue processing
                            logger.warning(
                                f"Skipping malformed streaming chunk: {line}"
                            )
                            continue
                    elif line.startswith(b"event: "):
                        # Handle event lines - Anthropic may send event types
                        continue
        
        except (AuthenticationError, RateLimitError):
            # Re-raise these specific errors
            raise
        except Exception as e:
            self.handle_provider_error(e, "streaming_request")