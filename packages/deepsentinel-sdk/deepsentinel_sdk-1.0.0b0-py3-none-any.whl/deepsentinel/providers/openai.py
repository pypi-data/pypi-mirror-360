"""OpenAI provider adapter for DeepSentinel.

This module implements the OpenAI provider adapter, supporting all OpenAI API
features including chat completions, text completions, embeddings, and more.
Includes comprehensive error handling, streaming support, and middleware.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import aiohttp
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
    StreamChunk,
)
from .base import BaseLLMProvider

# Configure logging
logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider adapter for DeepSentinel.

    This adapter provides comprehensive OpenAI API support with:
    - Chat and text completions with streaming
    - Embeddings generation
    - Audio transcription/translation
    - Image generation
    - Robust error handling with exponential backoff
    - Compliance middleware integration
    - Performance monitoring and logging
    
    Attributes:
        config: Provider configuration
        name: Provider name
        provider_type: Type of the provider (openai)
    """
    
    # OpenAI model constraints and defaults
    MAX_TOKENS_BY_MODEL = {
        "gpt-4": 8192,
        "gpt-4-0314": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0314": 32768,
        "gpt-4-32k-0613": 32768,
        "gpt-4-1106-preview": 128000,
        "gpt-4-vision-preview": 128000,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-0301": 4096,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo-16k-0613": 16384,
        "gpt-3.5-turbo-1106": 16385,
        "text-davinci-003": 4097,
        "text-davinci-002": 4097,
    }
    
    def __init__(self, config: ProviderConfig, name: str) -> None:
        """Initialize the OpenAI provider adapter.
        
        Args:
            config: Provider configuration
            name: Name identifier for this provider instance
        """
        super().__init__(config, name)
        self._session: Optional[ClientSession] = None
        self._semaphore = asyncio.Semaphore(
            self.config.extra_config.get("connection_limit", 20)
        )
        
        # Request tracking for performance monitoring
        self._request_count = 0
        self._total_tokens = 0
        self._last_reset_time = time.time()
        
        # Rate limiting tracking
        self._rate_limit_requests = 0
        self._rate_limit_tokens = 0
        self._rate_limit_reset_requests = 0
        self._rate_limit_reset_tokens = 0
        
        logger.info(
            f"Initialized OpenAI provider '{name}' with config: "
            f"timeout={config.timeout}s, max_retries={config.max_retries}"
        )
    
    async def initialize(self) -> None:
        """Initialize the OpenAI client and connection.
        
        This method sets up the aiohttp session for API calls, validates
        configuration, and performs initial connectivity tests.
        
        Raises:
            ProviderError: If initialization fails or API key is missing
            AuthenticationError: If API key is invalid
        """
        try:
            if not self.config.api_key:
                raise AuthenticationError(
                    "OpenAI API key is required for authentication",
                    provider_name=self.name,
                )
            
            # Initialize HTTP session if needed
            if self._session is None or self._session.closed:
                self._session = await self._get_http_session()
            
            # Perform initial health check to validate configuration
            try:
                await self.health_check()
                logger.info(
                    f"OpenAI provider '{self.name}' initialized successfully"
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
            error_msg = f"Failed to initialize OpenAI provider: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ProviderError(
                error_msg,
                provider_name=self.name,
                provider_error=e,
            ) from e
    
    async def _cleanup_provider_resources(self) -> None:
        """Clean up OpenAI provider-specific resources.
        
        Closes the aiohttp session and logs final statistics.
        """
        if self._session and not self._session.closed:
            await self._session.close()
        
        # Log final statistics
        logger.info(
            f"OpenAI provider '{self.name}' cleanup: "
            f"requests={self._request_count}, "
            f"total_tokens={self._total_tokens}"
        )
        
        self._initialized = False
    
    def _get_default_base_url(self) -> str:
        """Get the default base URL for the OpenAI API.
        
        Returns:
            Default OpenAI API base URL
        """
        return "https://api.openai.com/v1"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check on the OpenAI provider.
        
        Tests API connectivity, authentication, and model availability.
        
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
            # Test basic connectivity and authentication
            models = await self.list_models()
            
            health_status.update({
                "status": "healthy",
                "api_available": True,
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
                f"Health check passed for OpenAI provider '{self.name}'"
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
                f"Authentication failed for OpenAI provider '{self.name}': {e}"
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
                f"Health check failed for OpenAI provider '{self.name}': {e}"
            )
            return health_status
    
    async def chat_completion(
        self, request: ChatRequest, **kwargs: Any
    ) -> ChatResponse:
        """Create a chat completion using OpenAI API.
        
        Supports all OpenAI chat completion parameters with comprehensive
        error handling, validation, and performance monitoring.
        
        Args:
            request: Chat completion request
            **kwargs: Additional OpenAI-specific parameters
            
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
            payload = self._prepare_chat_payload(request, kwargs, stream=False)
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making chat completion request to OpenAI: "
                f"model={request.model}, messages={len(request.messages)}"
            )
            
            # Make the API request with retry logic
            async with self._semaphore:
                response_data = await self._make_api_request(
                    "post",
                    "/chat/completions",
                    json=payload,
                )
            
            # Update tracking metrics
            self._update_metrics(response_data, start_time)
            
            # Convert API response to ChatResponse
            response = ChatResponse(**response_data)
            
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
        """Create a streaming chat completion using OpenAI API.
        
        Provides real-time streaming of chat completion responses with
        proper error handling and chunk validation.
        
        Args:
            request: Chat completion request
            **kwargs: Additional OpenAI-specific parameters
            
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
            payload = self._prepare_chat_payload(request, kwargs, stream=True)
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making streaming chat completion request to OpenAI: "
                f"model={request.model}, messages={len(request.messages)}"
            )
            
            # Make the streaming API request
            async with self._semaphore:
                async for chunk_data in self._make_streaming_request(
                    "/chat/completions",
                    json=payload,
                ):
                    chunk_count += 1
                    try:
                        chunk = StreamChunk(**chunk_data)
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
        """Create a text completion using OpenAI API.
        
        Supports legacy text completion models with comprehensive
        error handling and validation.
        
        Args:
            request: Text completion request
            **kwargs: Additional OpenAI-specific parameters
            
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
            
            # Prepare the request payload
            payload = self._prepare_completion_payload(request, kwargs, False)
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making text completion request to OpenAI: "
                f"model={request.model}, prompt_length="
                f"{len(str(request.prompt)) if request.prompt else 0}"
            )
            
            # Make the API request with retry logic
            async with self._semaphore:
                response_data = await self._make_api_request(
                    "post",
                    "/completions",
                    json=payload,
                )
            
            # Update tracking metrics
            self._update_metrics(response_data, start_time)
            
            # Convert API response to CompletionResponse
            response = CompletionResponse(**response_data)
            
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
        """Create a streaming text completion using OpenAI API.
        
        Provides real-time streaming of text completion responses for
        legacy completion models.
        
        Args:
            request: Text completion request
            **kwargs: Additional OpenAI-specific parameters
            
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
            
            # Prepare the request payload
            payload = self._prepare_completion_payload(request, kwargs, True)
            
            # Log request (excluding sensitive data)
            logger.debug(
                f"Making streaming text completion request to OpenAI: "
                f"model={request.model}, prompt_length="
                f"{len(str(request.prompt)) if request.prompt else 0}"
            )
            
            # Make the streaming API request
            async with self._semaphore:
                async for chunk_data in self._make_streaming_request(
                    "/completions",
                    json=payload,
                ):
                    chunk_count += 1
                    try:
                        chunk = StreamChunk(**chunk_data)
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
        """Create embeddings for input text using OpenAI API.
        
        Supports all OpenAI embedding models with batch processing
        and comprehensive error handling.
        
        Args:
            request: Embedding request
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Embedding response containing vectors
            
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
            self._validate_embedding_request(request)
            
            # Prepare the request payload
            payload = request.dict(exclude_none=True)
            
            # Add any additional kwargs as parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            # Log request (excluding sensitive data)
            input_count = (
                len(request.input) if isinstance(request.input, list)
                else 1
            )
            logger.debug(
                f"Making embeddings request to OpenAI: "
                f"model={request.model}, inputs={input_count}"
            )
            
            # Make the API request with retry logic
            async with self._semaphore:
                response_data = await self._make_api_request(
                    "post",
                    "/embeddings",
                    json=payload,
                )
            
            # Update tracking metrics
            self._update_metrics(response_data, start_time)
            
            # Convert API response to EmbeddingResponse
            response = EmbeddingResponse(**response_data)
            
            logger.debug(
                f"Embeddings creation successful: "
                f"embeddings={len(response.data)}, "
                f"tokens="
                f"{response.usage.total_tokens if response.usage else 0}"
            )
            
            return response
        
        except Exception as e:
            # Log error with context
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                f"Embeddings creation failed after {duration_ms}ms: {str(e)}",
                exc_info=True
            )
            self.handle_provider_error(e, "create_embeddings")
            # This line should not be reached but keeps type checker happy
            raise ProviderError("Failed to create embeddings")
    
    async def list_models(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List available OpenAI models.
        
        Args:
            **kwargs: Additional parameters for the models list endpoint
            
        Returns:
            List of available models with metadata
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "get",
                    "/models",
                    params=kwargs,
                )
            
            # Extract the models list from the response
            return response.get("data", [])
        
        except Exception as e:
            self.handle_provider_error(e, "list_models")
            # This line should not be reached but keeps the type checker happy
            return []
    
    async def get_model(
        self, model_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get information about a specific OpenAI model.
        
        Args:
            model_id: ID of the model to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Model information and metadata
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "get",
                    f"/models/{model_id}",
                    params=kwargs,
                )
            
            return response
        
        except Exception as e:
            self.handle_provider_error(e, f"get_model({model_id})")
            # This line should not be reached but keeps the type checker happy
            return {}
    
    async def transcribe_audio(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text using OpenAI's Whisper API.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for transcription
            **kwargs: Additional parameters for the audio API
            
        Returns:
            Transcription result
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            form_data = aiohttp.FormData()
            
            # Add the file data
            if isinstance(audio_file, str):
                file_path = Path(audio_file)
                if not file_path.exists():
                    raise FileNotFoundError(
                        f"Audio file not found: {audio_file}"
                    )
                
                with open(file_path, "rb") as f:
                    form_data.add_field(
                        "file",
                        f.read(),
                        filename=file_path.name,
                        content_type="audio/mpeg"  # Adjust content type
                    )
            else:
                form_data.add_field(
                    "file",
                    audio_file,
                    filename="audio.mp3",  # Default filename
                    content_type="audio/mpeg"
                )
            
            # Add model and other parameters
            form_data.add_field("model", model)
            
            for key, value in kwargs.items():
                if value is not None:
                    form_data.add_field(key, str(value))
            
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "post",
                    "/audio/transcriptions",
                    data=form_data,
                )
            
            return response
        
        except Exception as e:
            self.handle_provider_error(e, "transcribe_audio")
            # This line should not be reached but keeps the type checker happy
            return {}
    
    async def translate_audio(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate audio to English text using OpenAI's Whisper API.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for translation
            **kwargs: Additional parameters for the audio API
            
        Returns:
            Translation result
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            form_data = aiohttp.FormData()
            
            # Add the file data
            if isinstance(audio_file, str):
                file_path = Path(audio_file)
                if not file_path.exists():
                    raise FileNotFoundError(
                        f"Audio file not found: {audio_file}"
                    )
                
                with open(file_path, "rb") as f:
                    form_data.add_field(
                        "file",
                        f.read(),
                        filename=file_path.name,
                        content_type="audio/mpeg"  # Adjust content type
                    )
            else:
                form_data.add_field(
                    "file",
                    audio_file,
                    filename="audio.mp3",  # Default filename
                    content_type="audio/mpeg"
                )
            
            # Add model and other parameters
            form_data.add_field("model", model)
            
            for key, value in kwargs.items():
                if value is not None:
                    form_data.add_field(key, str(value))
            
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "post",
                    "/audio/translations",
                    data=form_data,
                )
            
            return response
        
        except Exception as e:
            self.handle_provider_error(e, "translate_audio")
            # This line should not be reached but keeps the type checker happy
            return {}
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate images from text prompts using DALL-E.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use for generation (e.g., "dall-e-3")
            **kwargs: Additional parameters such as size, quality, style
            
        Returns:
            Image generation result containing URLs or base64 data
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            payload = {
                "prompt": prompt,
                "model": model,
                **{k: v for k, v in kwargs.items() if v is not None},
            }
            
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "post",
                    "/images/generations",
                    json=payload,
                )
            
            return response
        
        except Exception as e:
            self.handle_provider_error(e, "generate_image")
            # This line should not be reached but keeps the type checker happy
            return {}
    
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
            msg.role.value == "user" for msg in request.messages
        )
        if not has_user_message:
            raise ValidationError(
                "At least one user message is required",
                field_name="messages",
                field_value=[msg.role.value for msg in request.messages],
            )
    
    def _validate_completion_request(self, request: CompletionRequest) -> None:
        """Validate text completion request parameters.
        
        Args:
            request: Text completion request to validate
            
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
        
        # Validate prompt
        if not request.prompt:
            raise ValidationError(
                "Prompt is required for text completion",
                field_name="prompt",
                field_value=request.prompt,
            )
    
    def _validate_embedding_request(self, request: EmbeddingRequest) -> None:
        """Validate embedding request parameters.
        
        Args:
            request: Embedding request to validate
            
        Raises:
            ValidationError: If request parameters are invalid
        """
        # Validate input
        if not request.input:
            raise ValidationError(
                "Input is required for embeddings",
                field_name="input",
                field_value=request.input,
            )
        
        # Check input size limits
        if isinstance(request.input, list):
            if len(request.input) > 2048:  # OpenAI batch limit
                raise ValidationError(
                    f"Too many inputs ({len(request.input)}), "
                    "maximum is 2048",
                    field_name="input",
                    field_value=len(request.input),
                )
    
    def _prepare_chat_payload(
        self,
        request: ChatRequest,
        kwargs: Dict[str, Any],
        stream: bool,
    ) -> Dict[str, Any]:
        """Prepare chat completion request payload.
        
        Args:
            request: Chat completion request
            kwargs: Additional parameters
            stream: Whether this is a streaming request
            
        Returns:
            Prepared request payload
        """
        # Start with the request dict
        payload = request.dict(exclude_none=True)
        
        # Convert messages to the format expected by OpenAI
        payload["messages"] = [
            {
                "role": msg.role.value,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
                **(
                    {"function_call": msg.function_call}
                    if msg.function_call else {}
                ),
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **(
                    {"tool_call_id": msg.tool_call_id}
                    if msg.tool_call_id else {}
                ),
            }
            for msg in request.messages
        ]
        
        # Add additional kwargs
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        
        # Set streaming flag
        payload["stream"] = stream
        
        return payload
    
    def _prepare_completion_payload(
        self,
        request: CompletionRequest,
        kwargs: Dict[str, Any],
        stream: bool,
    ) -> Dict[str, Any]:
        """Prepare text completion request payload.
        
        Args:
            request: Text completion request
            kwargs: Additional parameters
            stream: Whether this is a streaming request
            
        Returns:
            Prepared request payload
        """
        # Start with the request dict
        payload = request.dict(exclude_none=True)
        
        # Add additional kwargs
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        
        # Set streaming flag
        payload["stream"] = stream
        
        return payload
    
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
            if "total_tokens" in usage:
                self._total_tokens += usage["total_tokens"]
        
        # Record performance metrics
        duration = time.time() - start_time
        self._record_request_metrics(duration, 0, success=True)
    
    def _extract_rate_limit_headers(self, headers: Any) -> None:
        """Extract rate limit information from response headers.
        
        Args:
            headers: Response headers
        """
        # Extract OpenAI rate limit headers
        self._rate_limit_requests = int(
            headers.get("x-ratelimit-remaining-requests", 0)
        )
        self._rate_limit_tokens = int(
            headers.get("x-ratelimit-remaining-tokens", 0)
        )
        
        # Extract reset times if available
        if "x-ratelimit-reset-requests" in headers:
            self._rate_limit_reset_requests = int(
                headers["x-ratelimit-reset-requests"]
            )
        if "x-ratelimit-reset-tokens" in headers:
            self._rate_limit_reset_tokens = int(
                headers["x-ratelimit-reset-tokens"]
            )
    
    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the OpenAI API with comprehensive error handling.
        
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
                        error_code = error_data.get("code")
                    except json.JSONDecodeError:
                        error_message = error_text
                        error_type = "unknown"
                        error_code = None
                    
                    # Handle specific error types
                    if response.status == 401:
                        raise AuthenticationError(
                            f"OpenAI authentication failed: {error_message}",
                            provider_name=self.name,
                            error_code=error_code,
                            details={"type": error_type},
                        )
                    elif response.status == 429:
                        retry_after = None
                        if "retry-after" in response.headers:
                            try:
                                retry_after = int(
                                    response.headers["retry-after"]
                                )
                            except ValueError:
                                pass
                        
                        raise RateLimitError(
                            f"OpenAI rate limit exceeded: {error_message}",
                            provider_name=self.name,
                            retry_after=retry_after,
                            error_code=error_code,
                            details={
                                "type": error_type,
                                "requests_remaining": (
                                    self._rate_limit_requests
                                ),
                                "tokens_remaining": self._rate_limit_tokens,
                            },
                        )
                    else:
                        raise ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=(
                                f"OpenAI API error: {error_message}"
                            ),
                            headers=response.headers,
                        )
                
                return await response.json()
        
        return await self._make_request_with_retry(request_func)
    
    async def _make_streaming_request(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Make a streaming request to the OpenAI API with error handling.
        
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
                        error_code = error_data.get("code")
                    except json.JSONDecodeError:
                        error_message = error_text
                        error_type = "unknown"
                        error_code = None
                    
                    # Handle specific error types
                    if response.status == 401:
                        raise AuthenticationError(
                            f"OpenAI authentication failed: {error_message}",
                            provider_name=self.name,
                            error_code=error_code,
                            details={"type": error_type},
                        )
                    elif response.status == 429:
                        retry_after = None
                        if "retry-after" in response.headers:
                            try:
                                retry_after = int(
                                    response.headers["retry-after"]
                                )
                            except ValueError:
                                pass
                        
                        raise RateLimitError(
                            f"OpenAI rate limit exceeded: {error_message}",
                            provider_name=self.name,
                            retry_after=retry_after,
                            error_code=error_code,
                            details={
                                "type": error_type,
                                "requests_remaining": (
                                    self._rate_limit_requests
                                ),
                                "tokens_remaining": self._rate_limit_tokens,
                            },
                        )
                    else:
                        raise ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"OpenAI API error: {error_message}",
                            headers=response.headers,
                        )
                
                # Process the streaming response
                async for line in response.content:
                    line = line.strip()
                    if not line or line == b"data: [DONE]":
                        continue
                    
                    if line.startswith(b"data: "):
                        try:
                            # Remove "data: " prefix
                            json_str = line[6:].decode("utf-8")
                            chunk = json.loads(json_str)
                            yield chunk
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # Skip malformed chunks but continue processing
                            logger.warning(
                                f"Skipping malformed streaming chunk: {line}"
                            )
                            continue
        
        except (AuthenticationError, RateLimitError):
            # Re-raise these specific errors
            raise
        except Exception as e:
            self.handle_provider_error(e, "streaming_request")