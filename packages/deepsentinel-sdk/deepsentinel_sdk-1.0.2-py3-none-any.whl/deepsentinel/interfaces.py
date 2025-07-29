"""DeepSentinel SDK API interfaces.

This module defines the abstract interfaces for different LLM operations
such as chat completions, text completions, embeddings, and streaming.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamChunk,
)


class BaseInterface(ABC):
    """Base interface for all LLM operations.
    
    This abstract base class defines common functionality and patterns
    that all specific interfaces should follow.
    """
    
    def __init__(self, client: Any) -> None:
        """Initialize the interface with a client reference.
        
        Args:
            client: Reference to the main SentinelClient instance
        """
        self._client = client
    
    @property
    def client(self) -> Any:
        """Get the client reference."""
        return self._client


class ChatInterface(BaseInterface):
    """Interface for chat completion operations.
    
    This interface handles conversational AI interactions with support
    for both synchronous and asynchronous operations, streaming responses,
    and compliance checking.
    """
    
    @abstractmethod
    async def create(
        self,
        request: ChatRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Create a chat completion.
        
        Args:
            request: Chat completion request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chat completion response
            
        Raises:
            ComplianceViolationError: If content violates policies
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    @abstractmethod
    async def create_stream(
        self,
        request: ChatRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming chat completion.
        
        Args:
            request: Chat completion request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ComplianceViolationError: If content violates policies
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    def create_sync(
        self,
        request: ChatRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> ChatResponse:
        """Create a chat completion synchronously.
        
        Args:
            request: Chat completion request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Chat completion response
        """
        return asyncio.run(self.create(request, provider, **kwargs))


class CompletionsInterface(BaseInterface):
    """Interface for text completion operations.
    
    This interface handles text completion requests with support for
    various completion parameters and compliance checking.
    """
    
    @abstractmethod
    async def create(
        self,
        request: CompletionRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Create a text completion.
        
        Args:
            request: Text completion request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Text completion response
            
        Raises:
            ComplianceViolationError: If content violates policies
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    @abstractmethod
    async def create_stream(
        self,
        request: CompletionRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming text completion.
        
        Args:
            request: Text completion request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ComplianceViolationError: If content violates policies
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    def create_sync(
        self,
        request: CompletionRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Create a text completion synchronously.
        
        Args:
            request: Text completion request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Text completion response
        """
        return asyncio.run(self.create(request, provider, **kwargs))


class EmbeddingsInterface(BaseInterface):
    """Interface for embedding operations.
    
    This interface handles text embedding generation with support for
    various embedding models and batch processing.
    """
    
    @abstractmethod
    async def create(
        self,
        request: EmbeddingRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> EmbeddingResponse:
        """Create embeddings for input text.
        
        Args:
            request: Embedding request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Embedding response containing vectors
            
        Raises:
            ComplianceViolationError: If content violates policies
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    def create_sync(
        self,
        request: EmbeddingRequest,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> EmbeddingResponse:
        """Create embeddings synchronously.
        
        Args:
            request: Embedding request
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Embedding response containing vectors
        """
        return asyncio.run(self.create(request, provider, **kwargs))


class ModelsInterface(BaseInterface):
    """Interface for model information and management.
    
    This interface provides access to available models, their capabilities,
    and metadata from different providers.
    """
    
    @abstractmethod
    async def list(
        self, provider: Optional[str] = None, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """List available models.
        
        Args:
            provider: Provider to query (queries default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of available models with metadata
            
        Raises:
            ProviderError: If provider operation fails
        """
        pass
    
    @abstractmethod
    async def retrieve(
        self,
        model_id: str,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Retrieve information about a specific model.
        
        Args:
            model_id: ID of the model to retrieve
            provider: Provider to query (queries default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Model information and metadata
            
        Raises:
            ProviderError: If provider operation fails
        """
        pass
    
    def list_sync(
        self, provider: Optional[str] = None, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """List available models synchronously.
        
        Args:
            provider: Provider to query (queries default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of available models with metadata
        """
        return asyncio.run(self.list(provider, **kwargs))
    
    def retrieve_sync(
        self,
        model_id: str,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Retrieve model information synchronously.
        
        Args:
            model_id: ID of the model to retrieve
            provider: Provider to query (queries default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Model information and metadata
        """
        return asyncio.run(self.retrieve(model_id, provider, **kwargs))


class AudioInterface(BaseInterface):
    """Interface for audio operations like transcription and text-to-speech.
    
    This interface handles audio-related AI operations with support for
    various audio formats and processing options.
    """
    
    @abstractmethod
    async def transcribe(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for transcription
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Transcription result
            
        Raises:
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    @abstractmethod
    async def translate(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate audio to English text.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for translation
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Translation result
            
        Raises:
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    def transcribe_sync(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio synchronously.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for transcription
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Transcription result
        """
        return asyncio.run(
            self.transcribe(audio_file, model, provider, **kwargs)
        )
    
    def translate_sync(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate audio synchronously.
        
        Args:
            audio_file: Path to audio file or audio bytes
            model: Model to use for translation
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Translation result
        """
        return asyncio.run(
            self.translate(audio_file, model, provider, **kwargs)
        )


class ImageInterface(BaseInterface):
    """Interface for image generation and processing operations.
    
    This interface handles image-related AI operations including
    generation, editing, and variation creation.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str = "dall-e-2",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate images from text prompts.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use for generation
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Image generation result
            
        Raises:
            ComplianceViolationError: If prompt violates policies
            ProviderError: If provider operation fails
            ValidationError: If request validation fails
        """
        pass
    
    def generate_sync(
        self,
        prompt: str,
        model: str = "dall-e-2",
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate images synchronously.
        
        Args:
            prompt: Text prompt for image generation
            model: Model to use for generation
            provider: Provider to use (uses default if None)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Image generation result
        """
        return asyncio.run(self.generate(prompt, model, provider, **kwargs))