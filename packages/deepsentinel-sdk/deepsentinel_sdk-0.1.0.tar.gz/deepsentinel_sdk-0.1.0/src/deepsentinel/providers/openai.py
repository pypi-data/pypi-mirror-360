"""OpenAI provider adapter for DeepSentinel.

This module implements the OpenAI provider adapter, supporting all OpenAI API
features including chat completions, text completions, embeddings, and more.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import aiohttp
from aiohttp import ClientResponseError, ClientSession

from ..config import ProviderConfig
from ..exceptions import ProviderError, ValidationError
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


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider adapter for DeepSentinel.

    This adapter supports OpenAI's API for chat and text completions,
    embeddings, audio transcription/translation, image generation, and model listing.
    
    Attributes:
        config: Provider configuration
        name: Provider name
        provider_type: Type of the provider (openai)
    """
    
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
    
    async def initialize(self) -> None:
        """Initialize the OpenAI client and connection.
        
        This method sets up the aiohttp session for API calls and validates
        that the API key is available.
        
        Raises:
            ProviderError: If initialization fails or API key is missing
        """
        try:
            if not self.config.api_key:
                raise ValueError("OpenAI API key is required")
            
            if self._session is None or self._session.closed:
                conn_kwargs = {}
                if self.config.extra_config.get("connection_timeout"):
                    conn_kwargs["timeout"] = aiohttp.ClientTimeout(
                        total=float(self.config.extra_config["connection_timeout"])
                    )
                
                self._session = aiohttp.ClientSession(**conn_kwargs)
            
            self._initialized = True
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize OpenAI provider: {str(e)}",
                provider_name=self.name,
                provider_error=e,
            ) from e
    
    async def cleanup(self) -> None:
        """Clean up resources used by the OpenAI provider.
        
        Closes the aiohttp session if it's open.
        """
        if self._session and not self._session.closed:
            await self._session.close()
        self._initialized = False
    
    def _get_default_base_url(self) -> str:
        """Get the default base URL for the OpenAI API.
        
        Returns:
            Default OpenAI API base URL
        """
        return "https://api.openai.com/v1"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the OpenAI provider.
        
        Checks API connectivity by making a simple models list request.
        
        Returns:
            Dictionary containing health status information
            
        Raises:
            ProviderError: If health check fails
        """
        try:
            # Try listing models as a simple health check
            models = await self.list_models(limit=1)
            return {
                "status": "healthy",
                "provider": self.provider_type.value,
                "api_available": True,
                "models_available": len(models) > 0,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_type.value,
                "error": str(e),
                "api_available": False,
            }
    
    async def chat_completion(
        self, request: ChatRequest, **kwargs: Any
    ) -> ChatResponse:
        """Create a chat completion using OpenAI API.
        
        Args:
            request: Chat completion request
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Chat completion response
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Prepare the request payload
            payload = request.dict(exclude_none=True)
            
            # Add any additional kwargs as parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            # Set stream to False for non-streaming request
            payload["stream"] = False
            
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "post",
                    "/chat/completions",
                    json=payload,
                )
            
            # Convert API response to ChatResponse
            return ChatResponse(**response)
        
        except Exception as e:
            self.handle_provider_error(e, "chat_completion")
            # This line should not be reached but keeps the type checker happy
            raise ProviderError("Failed to create chat completion")
    
    async def chat_completion_stream(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming chat completion using OpenAI API.
        
        Args:
            request: Chat completion request
            **kwargs: Additional OpenAI-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Prepare the request payload
            payload = request.dict(exclude_none=True)
            
            # Add any additional kwargs as parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            # Ensure stream is set to True
            payload["stream"] = True
            
            # Make the streaming API request
            async with self._semaphore:
                async for chunk in self._make_streaming_request(
                    "/chat/completions",
                    json=payload,
                ):
                    yield StreamChunk(**chunk)
        
        except Exception as e:
            self.handle_provider_error(e, "chat_completion_stream")
    
    async def text_completion(
        self, request: CompletionRequest, **kwargs: Any
    ) -> CompletionResponse:
        """Create a text completion using OpenAI API.
        
        Args:
            request: Text completion request
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Text completion response
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Prepare the request payload
            payload = request.dict(exclude_none=True)
            
            # Add any additional kwargs as parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            # Set stream to False for non-streaming request
            payload["stream"] = False
            
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "post",
                    "/completions",
                    json=payload,
                )
            
            # Convert API response to CompletionResponse
            return CompletionResponse(**response)
        
        except Exception as e:
            self.handle_provider_error(e, "text_completion")
            # This line should not be reached but keeps the type checker happy
            raise ProviderError("Failed to create text completion")
    
    async def text_completion_stream(
        self, request: CompletionRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming text completion using OpenAI API.
        
        Args:
            request: Text completion request
            **kwargs: Additional OpenAI-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Prepare the request payload
            payload = request.dict(exclude_none=True)
            
            # Add any additional kwargs as parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            # Ensure stream is set to True
            payload["stream"] = True
            
            # Make the streaming API request
            async with self._semaphore:
                async for chunk in self._make_streaming_request(
                    "/completions",
                    json=payload,
                ):
                    yield StreamChunk(**chunk)
        
        except Exception as e:
            self.handle_provider_error(e, "text_completion_stream")
    
    async def create_embeddings(
        self, request: EmbeddingRequest, **kwargs: Any
    ) -> EmbeddingResponse:
        """Create embeddings for input text using OpenAI API.
        
        Args:
            request: Embedding request
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Embedding response containing vectors
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Prepare the request payload
            payload = request.dict(exclude_none=True)
            
            # Add any additional kwargs as parameters
            for key, value in kwargs.items():
                if value is not None:
                    payload[key] = value
            
            # Make the API request with retry logic
            async with self._semaphore:
                response = await self._make_api_request(
                    "post",
                    "/embeddings",
                    json=payload,
                )
            
            # Convert API response to EmbeddingResponse
            return EmbeddingResponse(**response)
        
        except Exception as e:
            self.handle_provider_error(e, "create_embeddings")
            # This line should not be reached but keeps the type checker happy
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
                    raise FileNotFoundError(f"Audio file not found: {audio_file}")
                
                with open(file_path, "rb") as f:
                    form_data.add_field(
                        "file",
                        f.read(),
                        filename=file_path.name,
                        content_type="audio/mpeg"  # Adjust content type if needed
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
                    raise FileNotFoundError(f"Audio file not found: {audio_file}")
                
                with open(file_path, "rb") as f:
                    form_data.add_field(
                        "file",
                        f.read(),
                        filename=file_path.name,
                        content_type="audio/mpeg"  # Adjust content type if needed
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
    
    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the OpenAI API with retry logic.
        
        Args:
            method: HTTP method (get, post, etc.)
            endpoint: API endpoint path
            **kwargs: Additional parameters for the request
            
        Returns:
            Parsed JSON response
            
        Raises:
            ProviderError: If the request fails after retries
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
                if response.status >= 400:
                    error_text = await response.text()
                    try:
                        error_json = json.loads(error_text)
                        error_message = error_json.get("error", {}).get("message", error_text)
                    except json.JSONDecodeError:
                        error_message = error_text
                    
                    raise ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"OpenAI API error: {error_message}",
                        headers=response.headers,
                    )
                
                return await response.json()
        
        return await self._make_request_with_retry(request_func)
    
    async def _make_streaming_request(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Make a streaming request to the OpenAI API.
        
        Args:
            endpoint: API endpoint path
            **kwargs: Additional parameters for the request
            
        Yields:
            Parsed JSON chunks from the streaming response
            
        Raises:
            ProviderError: If the request fails
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
                if response.status >= 400:
                    error_text = await response.text()
                    try:
                        error_json = json.loads(error_text)
                        error_message = error_json.get("error", {}).get("message", error_text)
                    except json.JSONDecodeError:
                        error_message = error_text
                    
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
                            json_str = line[6:].decode("utf-8")  # Remove "data: " prefix
                            chunk = json.loads(json_str)
                            yield chunk
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            # Skip malformed chunks
                            continue
        
        except Exception as e:
            self.handle_provider_error(e, "streaming_request")