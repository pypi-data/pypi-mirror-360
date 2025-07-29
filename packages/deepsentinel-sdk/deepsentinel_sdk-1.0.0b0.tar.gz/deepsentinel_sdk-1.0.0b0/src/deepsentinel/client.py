"""DeepSentinel SDK main client implementation.

This module contains the main SentinelClient class that provides the primary
interface for interacting with LLM providers through the compliance middleware.
"""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import structlog

from .api.audit import AuditAPI
from .api.client import DeepSentinelAPIClient
from .api.compliance import ComplianceAPI
from .config import SentinelConfig
from .exceptions import DeepSentinelError
from .interfaces import (
    AudioInterface,
    ChatInterface,
    CompletionsInterface,
    EmbeddingsInterface,
    ImageInterface,
    ModelsInterface,
)
from .middleware.base import ComplianceMiddleware
from .providers.registry import ProviderRegistry, create_registry_from_config
from .types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
)


class SentinelClient:
    """Main client for the DeepSentinel SDK.
    
    This class provides the primary interface for interacting with LLM
    providers through a compliance-aware middleware layer. It handles
    configuration,
    provider management, compliance checking, and audit logging.
    
    Attributes:
        config: Client configuration
        chat: Chat completions interface
        completions: Text completions interface
        embeddings: Embeddings interface
        models: Models interface
        audio: Audio processing interface
        images: Image generation interface
    """
    
    def __init__(
        self,
        config: Optional[SentinelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Sentinel client.
        
        Args:
            config: Configuration instance (creates default if None)
            **kwargs: Additional configuration parameters
        """
        # Initialize configuration
        if config is None:
            config = SentinelConfig(**kwargs)
        elif kwargs:
            # Update config with additional parameters
            config.update_from_dict(kwargs)
        
        self.config = config
        
        # Initialize logging
        self._setup_logging()
        self.logger = structlog.get_logger(__name__)
        
        # Initialize components
        self._provider_registry: Optional[ProviderRegistry] = None
        self._middleware: Optional[ComplianceMiddleware] = None
        self._initialized = False
        
        # Initialize interfaces
        self.chat = SentinelChatInterface(self)
        self.completions = SentinelCompletionsInterface(self)
        self.embeddings = SentinelEmbeddingsInterface(self)
        self.models = SentinelModelsInterface(self)
        self.audio = SentinelAudioInterface(self)
        self.images = SentinelImageInterface(self)
    
    @property
    def provider_registry(self) -> ProviderRegistry:
        """Get the provider registry.
        
        Returns:
            Provider registry instance
            
        Raises:
            DeepSentinelError: If client is not initialized
        """
        if not self._initialized or self._provider_registry is None:
            raise DeepSentinelError("Client not initialized")
        return self._provider_registry
    
    @property
    def middleware(self) -> ComplianceMiddleware:
        """Get the compliance middleware.
        
        Returns:
            Compliance middleware instance
            
        Raises:
            DeepSentinelError: If client is not initialized
        """
        if not self._initialized or self._middleware is None:
            raise DeepSentinelError("Client not initialized")
        return self._middleware
    
    @property
    def is_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self._initialized
    
    def _setup_logging(self) -> None:
        """Set up structured logging based on configuration."""
        log_config = self.config.logging_config
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
                if log_config.structured
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Set log level
        logging.basicConfig(level=getattr(logging, log_config.level.upper()))
    
    async def initialize(self) -> None:
        """Initialize the client and all components.
        
        Raises:
            ConfigurationError: If configuration is invalid
            DeepSentinelError: If initialization fails
        """
        if self._initialized:
            return
        
        try:
            self.logger.info("Initializing DeepSentinel client")
            
            # Initialize provider registry
            self._provider_registry = await create_registry_from_config(
                self.config
            )
            
            # Initialize API client if enabled
            if self.config.api_integration_enabled and self.config.api_key:
                self._api_client = DeepSentinelAPIClient(self.config)
                await self._api_client.initialize()
                self.compliance_api = ComplianceAPI(self._api_client)
                self.audit_api = AuditAPI(self._api_client)
            
            # Initialize compliance middleware
            self._middleware = ComplianceMiddleware(self.config)
            await self._middleware.initialize()
            
            # Mark as initialized
            self._initialized = True
            
            self.logger.info(
                "DeepSentinel client initialized successfully",
                providers=len(self._provider_registry.providers),
                policies=len(self._middleware.policies),
            )
            
        except Exception as e:
            self.logger.error("Failed to initialize client", error=str(e))
            raise DeepSentinelError(
                f"Client initialization failed: {str(e)}"
            ) from e
    
    async def cleanup(self) -> None:
        """Clean up client resources."""
        if not self._initialized:
            return
        
        try:
            self.logger.info("Cleaning up DeepSentinel client")
            
            if self._provider_registry:
                await self._provider_registry.cleanup_all()
            
            # Clean up middleware
            if self._middleware:
                await self._middleware.cleanup()
                
            # Close API client if initialized
            if hasattr(self, '_api_client') and self._api_client:
                await self._api_client.close()
            
            self._initialized = False
            
            self.logger.info("DeepSentinel client cleanup completed")
            
        except Exception as e:
            self.logger.error("Error during client cleanup", error=str(e))
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on all components.
        
        Returns:
            Dictionary containing health status information
        """
        if not self._initialized:
            return {"status": "not_initialized"}
        
        try:
            # Check provider health
            provider_health = await self._provider_registry.health_check_all()
            
            # Overall status
            all_healthy = all(
                result.get("status") != "error"
                for result in provider_health.values()
            )
            
            # Get compliance engine health status
            compliance_engine = self._middleware._compliance_engine
            engine_health = await compliance_engine.health_check()
            
            return {
                "status": "healthy" if all_healthy else "degraded",
                "providers": provider_health,
                "middleware": {
                    "status": "healthy",
                    "policies": len(self._middleware.policies),
                    "engine": engine_health,
                },
                "config": {
                    "debug_mode": self.config.debug_mode,
                    "environment": self.config.environment,
                },
            }
            
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def __aenter__(self) -> "SentinelClient":
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.cleanup()
    
    def __repr__(self) -> str:
        """Return string representation of the client."""
        provider_count = (
            len(self._provider_registry.providers)
            if self._provider_registry
            else 0
        )
        return (
            f"SentinelClient("
            f"initialized={self._initialized}, "
            f"providers={provider_count}, "
            f"environment='{self.config.environment}')"
        )


class SentinelChatInterface(ChatInterface):
    """Chat completions interface implementation."""
    
    async def create(
        self,
        request: ChatRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Create a chat completion."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        # Process request through middleware
        context = {
            "provider": provider,
            "operation": "chat.create",
            **kwargs
        }
        processed_request = await self.client.middleware.process_request(
            request, context
        )
        
        # Get provider and make request
        provider_adapter = self.client.provider_registry.get_provider(provider)
        response = await provider_adapter.chat_completion(
            processed_request, **kwargs
        )
        
        # Process response through middleware
        processed_response = await self.client.middleware.process_response(
            response, processed_request, {"provider": provider}
        )
        
        return processed_response
    
    async def create_stream(
        self,
        request: ChatRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming chat completion."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        # Process request through middleware
        context = {
            "provider": provider,
            "operation": "chat.create_stream",
            **kwargs
        }
        processed_request = await self.client.middleware.process_request(
            request, context
        )
        
        # Get provider and make streaming request
        provider_adapter = self.client.provider_registry.get_provider(provider)
        
        async for chunk in provider_adapter.chat_completion_stream(
            processed_request, **kwargs
        ):
            # Note: For streaming, we typically don't run full compliance
            # checks on each chunk for performance reasons
            yield chunk


class SentinelCompletionsInterface(CompletionsInterface):
    """Text completions interface implementation."""
    
    async def create(
        self,
        request: CompletionRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Create a text completion."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        # Process request through middleware
        context = {
            "provider": provider,
            "operation": "completions.create",
            **kwargs
        }
        processed_request = await self.client.middleware.process_request(
            request, context
        )
        
        # Get provider and make request
        provider_adapter = self.client.provider_registry.get_provider(provider)
        response = await provider_adapter.text_completion(
            processed_request, **kwargs
        )
        
        # Process response through middleware
        processed_response = await self.client.middleware.process_response(
            response, processed_request, {"provider": provider}
        )
        
        return processed_response
    
    async def create_stream(
        self,
        request: CompletionRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming text completion."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        # Process request through middleware
        context = {
            "provider": provider,
            "operation": "completions.create_stream",
            **kwargs
        }
        processed_request = await self.client.middleware.process_request(
            request, context
        )
        
        # Get provider and make streaming request
        provider_adapter = self.client.provider_registry.get_provider(provider)
        
        async for chunk in provider_adapter.text_completion_stream(
            processed_request, **kwargs
        ):
            yield chunk


class SentinelEmbeddingsInterface(EmbeddingsInterface):
    """Embeddings interface implementation."""
    
    async def create(
        self,
        request: EmbeddingRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> EmbeddingResponse:
        """Create embeddings."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        # Process request through middleware
        context = {
            "provider": provider,
            "operation": "embeddings.create",
            **kwargs
        }
        processed_request = await self.client.middleware.process_request(
            request, context
        )
        
        # Get provider and make request
        provider_adapter = self.client.provider_registry.get_provider(provider)
        response = await provider_adapter.create_embeddings(
            processed_request, **kwargs
        )
        
        # Process response through middleware
        processed_response = await self.client.middleware.process_response(
            response, processed_request, {"provider": provider}
        )
        
        return processed_response


class SentinelModelsInterface(ModelsInterface):
    """Models interface implementation."""
    
    async def list(
        self, provider: Optional[str] = None, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """List available models."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        provider_adapter = self.client.provider_registry.get_provider(provider)
        return await provider_adapter.list_models(**kwargs)
    
    async def retrieve(
        self,
        model_id: str,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Retrieve model information."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        provider_adapter = self.client.provider_registry.get_provider(provider)
        return await provider_adapter.get_model(model_id, **kwargs)


class SentinelAudioInterface(AudioInterface):
    """Audio interface implementation."""
    
    async def transcribe(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        provider_adapter = self.client.provider_registry.get_provider(provider)
        return await provider_adapter.transcribe_audio(
            audio_file, model, **kwargs
        )
    
    async def translate(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate audio to English text."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        provider_adapter = self.client.provider_registry.get_provider(provider)
        return await provider_adapter.translate_audio(
            audio_file, model, **kwargs
        )


class SentinelImageInterface(ImageInterface):
    """Image interface implementation."""
    
    async def generate(
        self,
        prompt: str,
        model: str = "dall-e-2",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate images from text prompts."""
        if not self.client.is_initialized:
            await self.client.initialize()
        
        provider_adapter = self.client.provider_registry.get_provider(provider)
        return await provider_adapter.generate_image(prompt, model, **kwargs)