"""Anthropic provider adapter for DeepSentinel.

This module implements the Anthropic provider adapter, supporting Claude models
for chat completions with streaming support.
"""

import asyncio
import json
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp
from aiohttp import ClientResponseError, ClientSession

from ..config import ProviderConfig
from ..exceptions import ProviderError
from ..types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    MessageRole,
    StreamChunk,
)
from .base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider adapter for DeepSentinel.

    This adapter supports Anthropic's Claude models for chat completions,
    with message role handling and streaming support.
    
    Attributes:
        config: Provider configuration
        name: Provider name
        provider_type: Type of the provider (anthropic)
    """
    
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
    
    async def initialize(self) -> None:
        """Initialize the Anthropic client and connection.
        
        This method sets up the aiohttp session for API calls and validates
        that the API key is available.
        
        Raises:
            ProviderError: If initialization fails or API key is missing
        """
        try:
            if not self.config.api_key:
                raise ValueError("Anthropic API key is required")
            
            if self._session is None or self._session.closed:
                conn_kwargs = {}
                timeout = self.config.extra_config.get("connection_timeout")
                if timeout:
                    conn_kwargs["timeout"] = aiohttp.ClientTimeout(
                        total=float(timeout)
                    )
                
                self._session = aiohttp.ClientSession(**conn_kwargs)
            
            self._initialized = True
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize Anthropic provider: {str(e)}",
                provider_name=self.name,
                provider_error=e,
            ) from e
    
    async def cleanup(self) -> None:
        """Clean up resources used by the Anthropic provider.
        
        Closes the aiohttp session if it's open.
        """
        if self._session and not self._session.closed:
            await self._session.close()
        self._initialized = False
    
    def _get_default_base_url(self) -> str:
        """Get the default base URL for the Anthropic API.
        
        Returns:
            Default Anthropic API base URL
        """
        return "https://api.anthropic.com"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the Anthropic provider.
        
        Tests API connectivity by making a minimal API request.
        
        Returns:
            Dictionary containing health status information
            
        Raises:
            ProviderError: If health check fails
        """
        try:
            # Make a minimal request to verify API connectivity
            # Anthropic doesn't have a specific health check endpoint,
            # so we'll make a minimal completion request
            test_request = ChatRequest(
                messages=[{
                    "role": MessageRole.USER,
                    "content": "Hello",
                }],
                model="claude-instant-1",
                max_tokens=1,
            )
            
            # Just check if we can access the API, don't complete the request
            headers = self._prepare_headers()
            url = self._build_request_url("/v1/messages")
            
            async with self._session.post(
                url, 
                headers=headers,
                json=self._prepare_chat_payload(test_request),
                timeout=5,
            ) as response:
                status = response.status
            
            return {
                "status": "healthy" if status < 400 else "unhealthy",
                "provider": self.provider_type.value,
                "api_available": status < 400,
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
        """Create a chat completion using Anthropic API.
        
        Args:
            request: Chat completion request
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            Chat completion response
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Convert the request to Anthropic format
            payload = self._prepare_chat_payload(request, **kwargs)
            
            # Set stream to False for non-streaming request
            payload["stream"] = False
            
            # Make the API request with retry logic
            async with self._semaphore:
                anthropic_response = await self._make_api_request(
                    "post",
                    "/v1/messages",
                    json=payload,
                )
            
            # Convert Anthropic API response to standard ChatResponse
            response = self._convert_anthropic_response(
                anthropic_response, request.model
            )
            
            return response
        
        except Exception as e:
            self.handle_provider_error(e, "chat_completion")
            # This line should not be reached but keeps the type checker happy
            raise ProviderError("Failed to create chat completion")
    
    async def chat_completion_stream(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming chat completion using Anthropic API.
        
        Args:
            request: Chat completion request
            **kwargs: Additional Anthropic-specific parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
        """
        try:
            self.validate_request(request)
            
            # Convert the request to Anthropic format
            payload = self._prepare_chat_payload(request, **kwargs)
            
            # Ensure stream is set to True
            payload["stream"] = True
            
            # Make the streaming API request
            async with self._semaphore:
                async for chunk in self._make_streaming_request(
                    "/v1/messages",
                    json=payload,
                ):
                    # Convert Anthropic streaming format to our standard format
                    standard_chunk = self._convert_anthropic_stream_chunk(
                        chunk, request.model
                    )
                    if standard_chunk:
                        yield standard_chunk
        
        except Exception as e:
            self.handle_provider_error(e, "chat_completion_stream")
    
    async def text_completion(
        self, request: CompletionRequest, **kwargs: Any
    ) -> CompletionResponse:
        """Create a text completion using Anthropic API.
        
        Note: Anthropic doesn't support traditional text completions,
        so this method emulates it by using chat completions with a user message.
        
        Args:
            request: Text completion request
            **kwargs: Additional parameters
            
        Returns:
            Text completion response
            
        Raises:
            ProviderError: If the operation fails
        """
        # Convert text completion request to chat completion
        chat_request = ChatRequest(
            messages=[
                {
                    "role": MessageRole.USER,
                    "content": request.prompt if isinstance(request.prompt, str) 
                               else "\n".join(request.prompt),
                }
            ],
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop=request.stop,
            stream=False,
            user=request.user,
        )
        
        try:
            # Use the chat_completion method
            chat_response = await self.chat_completion(chat_request, **kwargs)
            
            # Convert chat response to text completion response format
            choices = []
            for idx, choice in enumerate(chat_response.choices):
                text = choice.message.content or ""
                choices.append({
                    "text": text,
                    "index": idx,
                    "finish_reason": choice.finish_reason,
                })
            
            return CompletionResponse(
                id=chat_response.id,
                object="text_completion",
                created=chat_response.created,
                model=chat_response.model,
                choices=choices,
                usage=chat_response.usage,
            )
        
        except Exception as e:
            self.handle_provider_error(e, "text_completion")
            # This line should not be reached but keeps the type checker happy
            raise ProviderError("Failed to create text completion")
    
    async def text_completion_stream(
        self, request: CompletionRequest, **kwargs: Any
    ) -> AsyncIterator[StreamChunk]:
        """Create a streaming text completion using Anthropic API.
        
        Note: Anthropic doesn't support traditional text completions,
        so this method emulates it by using chat completions with a user message.
        
        Args:
            request: Text completion request
            **kwargs: Additional parameters
            
        Yields:
            Stream chunks containing partial responses
            
        Raises:
            ProviderError: If the operation fails
        """
        # Convert text completion request to chat completion
        chat_request = ChatRequest(
            messages=[
                {
                    "role": MessageRole.USER,
                    "content": request.prompt if isinstance(request.prompt, str) 
                               else "\n".join(request.prompt),
                }
            ],
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop=request.stop,
            stream=True,
            user=request.user,
        )
        
        try:
            # Use the chat_completion_stream method but convert chunks
            async for chunk in self.chat_completion_stream(chat_request, **kwargs):
                # Convert chat stream format to text completion stream format
                converted_chunk = self._convert_chat_to_text_stream_chunk(chunk)
                if converted_chunk:
                    yield converted_chunk
        
        except Exception as e:
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
            "Embeddings are not supported by the Anthropic provider",
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
                "created": 1709251200,
                "description": "Most powerful Claude model for highly complex tasks",
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "created": 1709251200,
                "description": "Balanced Claude model for enterprise workloads",
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "created": 1709769600,
                "description": "Fastest and most compact Claude model",
            },
            {
                "id": "claude-2.1",
                "name": "Claude 2.1",
                "created": 1699574400,
                "description": "Previous generation Claude model",
            },
            {
                "id": "claude-2.0",
                "name": "Claude 2",
                "created": 1689120000,
                "description": "Previous generation Claude model",
            },
            {
                "id": "claude-instant-1.2",
                "name": "Claude Instant 1.2",
                "created": 1679616000,
                "description": "Fast, affordable Claude model",
            },
        ]
        
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
                return model
        
        raise ProviderError(
            f"Unknown model: {model_id}",
            provider_name=self.name,
        )
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for Anthropic API requests.
        
        Returns:
            Dictionary of headers to include in requests
        """
        headers = super()._prepare_headers()
        
        # Anthropic uses a different auth header format
        if self.config.api_key:
            headers["x-api-key"] = self.config.api_key
            # Remove the Bearer token that the base class might have added
            headers.pop("Authorization", None)
        
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
            "max_tokens": request.max_tokens if request.max_tokens is not None else 1024,
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
        
        # Process messages
        system_prompt = None
        messages = []
        
        # Extract system prompt and convert message format
        for msg in request.messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
            elif msg.role in (MessageRole.USER, MessageRole.ASSISTANT):
                messages.append({
                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                    "content": msg.content,
                })
        
        # Add system prompt if present
        if system_prompt:
            payload["system"] = system_prompt
        
        # Add messages
        payload["messages"] = messages
        
        # Add tool/function calling if present
        if request.tools:
            payload["tools"] = request.tools
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice
            
        # Add any additional kwargs as parameters
        for key, value in kwargs.items():
            if value is not None and key not in payload:
                payload[key] = value
                
        return payload
    
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
        # Extract the message content
        message_content = response.get("content", [])
        text_content = ""
        
        # Process the content blocks (Anthropic returns content as blocks)
        for block in message_content:
            if block.get("type") == "text":
                text_content += block.get("text", "")
        
        # Create a standard ChatResponse
        return ChatResponse(
            id=response.get("id", ""),
            object="chat.completion",
            created=int(response.get("created_at", 0)),
            model=model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": MessageRole.ASSISTANT,
                        "content": text_content,
                    },
                    "finish_reason": response.get("stop_reason", "stop"),
                }
            ],
            usage={
                "prompt_tokens": response.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": response.get("usage", {}).get("output_tokens", 0),
                "total_tokens": (
                    response.get("usage", {}).get("input_tokens", 0) +
                    response.get("usage", {}).get("output_tokens", 0)
                ),
            },
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
        # Skip non-content chunks
        if "type" not in chunk or chunk["type"] != "content_block_delta":
            return None
        
        # Extract the content delta
        delta = chunk.get("delta", {}).get("text", "")
        
        # Create a standard StreamChunk
        return StreamChunk(
            id=chunk.get("message_id", ""),
            object="chat.completion.chunk",
            created=int(chunk.get("created_at", 0)),
            model=model,
            choices=[
                {
                    "index": 0,
                    "delta": {
                        "role": MessageRole.ASSISTANT,
                        "content": delta,
                    },
                    "finish_reason": None,
                }
            ],
        )
    
    def _convert_chat_to_text_stream_chunk(
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
        content = ""
        for choice in chunk.choices:
            if "delta" in choice and "content" in choice["delta"]:
                content = choice["delta"]["content"]
            
        # Create a text completion chunk format
        return StreamChunk(
            id=chunk.id,
            object="text_completion.chunk",
            created=chunk.created,
            model=chunk.model,
            choices=[
                {
                    "index": 0,
                    "text": content,
                    "finish_reason": choice.get("finish_reason"),
                }
                for choice in chunk.choices
            ],
        )
    
    async def _make_api_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the Anthropic API with retry logic.
        
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
                        error_message = error_json.get(
                            "error", {}
                        ).get("message", error_text)
                    except json.JSONDecodeError:
                        error_message = error_text
                    
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
        """Make a streaming request to the Anthropic API.
        
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
                        error_message = error_json.get(
                            "error", {}
                        ).get("message", error_text)
                    except json.JSONDecodeError:
                        error_message = error_text
                    
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
                    if not line or line == b"data: [DONE]":
                        continue
                    
                    if line.startswith(b"data: "):
                        try:
                            # Remove "data: " prefix
                            json_str = line[6:].decode("utf-8")  
                            chunk = json.loads(json_str)
                            yield chunk
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # Skip malformed chunks
                            continue
        
        except Exception as e:
            self.handle_provider_error(e, "streaming_request")