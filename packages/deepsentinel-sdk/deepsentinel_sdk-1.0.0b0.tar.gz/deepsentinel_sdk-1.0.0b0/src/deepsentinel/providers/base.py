"""Base provider adapter for LLM integrations.

This module defines the abstract base class for all provider adapters,
establishing a consistent interface for different LLM providers.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import aiohttp

from ..config import ProviderConfig
from ..exceptions import ProviderError
from ..types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
)


class ProviderAdapter(ABC):
    """Abstract base class for all LLM provider adapters.
    
    This class defines the interface that all provider implementations
    must follow, ensuring consistent behavior across different providers.
    
    Attributes:
        config: Provider configuration
        name: Provider name
        provider_type: Type of the provider
    """
    
    def __init__(self, config: ProviderConfig, name: str) -> None:
        """Initialize the provider adapter.
        
        Args:
            config: Provider configuration
            name: Name identifier for this provider instance
        """
        self.config = config
        self.name = name
        self.provider_type = config.provider_type
        self._client: Optional[Any] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialized = False
    
    @property
    def client(self) -> Any:
        """Get the underlying provider client.
        
        Returns:
            The provider's client instance
            
        Raises:
            ProviderError: If the provider is not initialized
        """
        if not self._initialized or self._client is None:
            raise ProviderError(
                f"Provider '{self.name}' is not initialized",
                provider_name=self.name,
            )
        return self._client
    
    @property
    def is_initialized(self) -> bool:
        """Check if the provider is initialized."""
        return self._initialized
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider client and connection.
        
        This method should set up the provider client, validate
        configuration, and establish any necessary connections.
        
        Raises:
            ProviderError: If initialization fails
        """
        pass
    
    async def cleanup(self) -> None:
        """Clean up provider resources.
        
        This method should close connections, clean up resources,
        and prepare the provider for shutdown.
        """
        if self._session and not self._session.closed:
            await self._session.close()
        await self._cleanup_provider_resources()
    
    @abstractmethod
    async def _cleanup_provider_resources(self) -> None:
        """Clean up provider-specific resources."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the provider.
        
        Returns:
            Dictionary containing health status information
            
        Raises:
            ProviderError: If health check fails
        """
        pass
    
    @abstractmethod
    async def chat_completion(
        self, request: ChatRequest, **kwargs: Any
    ) -> ChatResponse:
        """Create a chat completion.
        
        Args:
            request: Chat completion request
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chat completion response
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming chat completion.
        
        Args:
            request: Chat completion request
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    @abstractmethod
    async def text_completion(
        self, request: CompletionRequest, **kwargs: Any
    ) -> CompletionResponse:
        """Create a text completion.
        
        Args:
            request: Text completion request
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Text completion response
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    @abstractmethod
    async def text_completion_stream(
        self, request: CompletionRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming text completion.
        
        Args:
            request: Text completion request
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    @abstractmethod
    async def create_embeddings(
        self, request: EmbeddingRequest, **kwargs: Any
    ) -> EmbeddingResponse:
        """Create embeddings for input text.
        
        Args:
            request: Embedding request
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Embedding response containing vectors
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    @abstractmethod
    async def list_models(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List available models.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of available models with metadata
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    @abstractmethod
    async def get_model(
        self, model_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get information about a specific model.
        
        Args:
            model_id: ID of the model to retrieve
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Model information and metadata
            
        Raises:
            ProviderError: If the operation fails
        """
        pass
    
    async def transcribe_audio(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for transcription
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Transcription result
            
        Raises:
            ProviderError: If the operation fails or is not supported
        """
        raise ProviderError(
            f"Audio transcription not supported by provider '{self.name}'",
            provider_name=self.name,
        )
    
    async def translate_audio(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate audio to English text.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for translation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Translation result
            
        Raises:
            ProviderError: If the operation fails or is not supported
        """
        raise ProviderError(
            f"Audio translation not supported by provider '{self.name}'",
            provider_name=self.name,
        )
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-2",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate images from text prompts.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use for generation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Image generation result
            
        Raises:
            ProviderError: If the operation fails or is not supported
        """
        raise ProviderError(
            f"Image generation not supported by provider '{self.name}'",
            provider_name=self.name,
        )
    
    def validate_request(self, request: Any) -> None:
        """Validate a request before processing.
        
        Args:
            request: Request to validate
            
        Raises:
            ValidationError: If the request is invalid
        """
        # Basic validation - subclasses can override for provider-specific
        # validation
        if hasattr(request, 'model_validate'):
            request.model_validate(request.dict())
    
    def handle_provider_error(self, error: Exception, operation: str) -> None:
        """Handle and wrap provider-specific errors.
        
        Args:
            error: The original error from the provider
            operation: The operation that failed
            
        Raises:
            ProviderError: Wrapped provider error
        """
        if isinstance(error, ProviderError):
            raise error
        
        raise ProviderError(
            f"Provider '{self.name}' failed during {operation}: {str(error)}",
            provider_name=self.name,
            provider_error=error,
        )
    
    async def __aenter__(self) -> "ProviderAdapter":
        """Async context manager entry."""
        if not self._initialized:
            await self.initialize()
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.cleanup()
    
    def __repr__(self) -> str:
        """Return string representation of the provider."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"type='{self.provider_type}', "
            f"initialized={self._initialized})"
        )


class BaseLLMProvider(ProviderAdapter):
    """Base class for LLM providers with common functionality.
    
    This class provides common implementations and utilities that
    most LLM providers can use, reducing code duplication.
    """
    
    def __init__(self, config: ProviderConfig, name: str) -> None:
        """Initialize the base LLM provider.
        
        Args:
            config: Provider configuration
            name: Name identifier for this provider instance
        """
        super().__init__(config, name)
        self._request_timeout = config.timeout
        self._max_retries = config.max_retries
        self._retry_delay = config.retry_delay
        self._performance_metrics = {}
    
    async def _get_http_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling.
        
        Returns:
            aiohttp.ClientSession with connection pooling configured
        """
        if self._session is None or self._session.closed:
            # Connection pool settings
            connector = aiohttp.TCPConnector(
                limit=getattr(self.config, 'connection_pool_size', 100),
                limit_per_host=getattr(
                    self.config, 'connection_pool_per_host', 20
                ),
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )
            
            # Session timeout configuration
            timeout = aiohttp.ClientTimeout(
                total=self._request_timeout,
                connect=getattr(self.config, 'connect_timeout', 10),
                sock_read=getattr(self.config, 'read_timeout', 30),
            )
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self._prepare_headers(),
                trust_env=True,
            )
        
        return self._session
    
    async def _make_request_with_retry(
        self,
        request_func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Make a request with retry logic and performance tracking.
        
        Args:
            request_func: Function to call for the request
            *args: Positional arguments for the request function
            **kwargs: Keyword arguments for the request function
            
        Returns:
            Result of the request function
            
        Raises:
            ProviderError: If all retries are exhausted
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(self._max_retries + 1):
            try:
                result = await request_func(*args, **kwargs)
                
                # Track performance metrics
                duration = time.time() - start_time
                self._record_request_metrics(duration, attempt, success=True)
                
                return result
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                    continue
                break
        
        # Track failed request metrics
        duration = time.time() - start_time
        self._record_request_metrics(
            duration, self._max_retries, success=False
        )
        
        self.handle_provider_error(
            last_error or Exception("Unknown error"),
            "request with retry"
        )
    
    def _record_request_metrics(
        self, duration: float, attempts: int, success: bool
    ) -> None:
        """Record request performance metrics.
        
        Args:
            duration: Request duration in seconds
            attempts: Number of attempts made
            success: Whether the request was successful
        """
        if "requests" not in self._performance_metrics:
            self._performance_metrics["requests"] = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "total_duration": 0.0,
                "avg_duration": 0.0,
                "retry_count": 0,
            }
        
        metrics = self._performance_metrics["requests"]
        metrics["total"] += 1
        metrics["total_duration"] += duration
        metrics["avg_duration"] = metrics["total_duration"] / metrics["total"]
        
        if success:
            metrics["successful"] += 1
        else:
            metrics["failed"] += 1
        
        if attempts > 0:
            metrics["retry_count"] += attempts
    
    async def _cleanup_provider_resources(self) -> None:
        """Clean up provider-specific resources."""
        # Base implementation does nothing - subclasses can override
        pass
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this provider.
        
        Returns:
            Dictionary containing performance metrics
        """
        return self._performance_metrics.copy()
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for requests.
        
        Returns:
            Dictionary of headers to include in requests
        """
        headers = {
            "User-Agent": f"DeepSentinel-SDK/0.1.0 ({self.provider_type})",
            **self.config.headers,
        }
        
        if self.config.api_key:
            # Most providers use Bearer token auth
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        return headers
    
    def _build_request_url(self, endpoint: str) -> str:
        """Build the full request URL.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL for the request
        """
        base_url = self.config.base_url or self._get_default_base_url()
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    @abstractmethod
    def _get_default_base_url(self) -> str:
        """Get the default base URL for this provider.
        
        Returns:
            Default base URL string
        """
        pass