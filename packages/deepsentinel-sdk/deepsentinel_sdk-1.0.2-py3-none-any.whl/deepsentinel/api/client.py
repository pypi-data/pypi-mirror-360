"""Main API client for DeepSentinel compliance services.

This module provides the core HTTP client functionality for communicating
with DeepSentinel's compliance API services.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

import aiohttp
import structlog

from ..config import SentinelConfig
from ..exceptions import (
    AuthenticationError,
    DeepSentinelError,
    RateLimitError,
    ValidationError,
)


class DeepSentinelAPIClient:
    """Main API client for DeepSentinel compliance services.
    
    This class handles authentication, request/response management,
    rate limiting, and communication with DeepSentinel's API endpoints.
    
    Attributes:
        config: Sentinel configuration
        logger: Structured logger
        base_url: Base URL for API requests
        session: Aiohttp client session
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the API client.
        
        Args:
            config: Sentinel configuration
        """
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # API configuration
        self.base_url = (
            config.api_base_url or "https://api.deepsentinel.com/v1"
        )
        self._api_key = config.api_key
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limiter = self._create_rate_limiter()
        
        self.logger.info(
            "DeepSentinel API client initialized",
            base_url=self.base_url,
        )
    
    async def initialize(self) -> None:
        """Initialize client session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers=self._get_default_headers(),
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            )
    
    async def close(self) -> None:
        """Close client session."""
        if self._session is not None:
            await self._session.close()
            self._session = None
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests.
        
        Returns:
            Dictionary of default headers
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"deepsentinel-python/{self.config.version}",
            "Accept": "application/json",
        }
        
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        
        return headers
    
    def _create_rate_limiter(self) -> Any:
        """Create rate limiter based on configuration.
        
        Returns:
            Rate limiter instance
        """
        # Simple rate limiting implementation
        # TODO: Replace with more sophisticated rate limiting
        class SimpleRateLimiter:
            def __init__(self, max_requests: int, time_window: float) -> None:
                self.max_requests = max_requests
                self.time_window = time_window
                self.requests: List[float] = []
                self.lock = asyncio.Lock()
            
            async def acquire(self) -> None:
                async with self.lock:
                    now = asyncio.get_event_loop().time()
                    
                    # Remove expired timestamps
                    self.requests = [
                        ts for ts in self.requests
                        if now - ts < self.time_window
                    ]
                    
                    if len(self.requests) >= self.max_requests:
                        wait_time = (
                            self.time_window - (now - min(self.requests))
                        )
                        if wait_time > 0:
                            raise RateLimitError(
                                (
                                    f"Rate limit exceeded. "
                                    f"Retry after {wait_time:.2f}s"
                                ),
                                retry_after=wait_time,
                            )
                    
                    # Add current timestamp
                    self.requests.append(now)
        
        return SimpleRateLimiter(
            max_requests=self.config.api_rate_limit or 100,
            time_window=self.config.api_rate_window or 60.0,
        )
    
    async def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """Make an API request.
        
        Args:
            method: HTTP method
            path: API path
            data: Request data
            params: URL parameters
            headers: Additional headers
            timeout: Request timeout
            retry_count: Current retry count
            
        Returns:
            API response
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            ValidationError: If request validation fails
            DeepSentinelError: For other API errors
        """
        await self.initialize()
        
        if self._session is None:
            raise DeepSentinelError("API client session not initialized")
        
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._get_default_headers()
        
        if headers:
            request_headers.update(headers)
        
        request_kwargs = {
            "headers": request_headers,
            "params": params,
        }
        
        if timeout:
            request_kwargs["timeout"] = aiohttp.ClientTimeout(total=timeout)
        
        if data is not None:
            request_kwargs["json"] = data
        
        max_retries = self.config.max_retries or 3
        retry_codes = [429, 500, 502, 503, 504]
        retry_delay = self.config.retry_delay or 1.0
        
        try:
            # Check rate limiting
            await self._rate_limiter.acquire()
            
            self.logger.debug(
                "Making API request",
                method=method,
                url=url,
                retry_count=retry_count,
            )
            
            async with self._session.request(
                method, url, **request_kwargs
            ) as response:
                response_data = await response.text()
                
                try:
                    response_json = json.loads(response_data)
                except json.JSONDecodeError:
                    response_json = {"error": {"message": response_data}}
                
                if response.status == 200:
                    return response_json
                
                # Handle retryable errors
                if (
                    response.status in retry_codes and
                    retry_count < max_retries
                ):
                    # Exponential backoff
                    backoff_delay = retry_delay * (2 ** retry_count)
                    
                    self.logger.warning(
                        "Retrying API request",
                        method=method,
                        url=url,
                        status=response.status,
                        retry_count=retry_count,
                        backoff_delay=backoff_delay,
                    )
                    
                    await asyncio.sleep(backoff_delay)
                    return await self.request(
                        method,
                        path,
                        data=data,
                        params=params,
                        headers=headers,
                        timeout=timeout,
                        retry_count=retry_count + 1,
                    )
                
                # Handle specific error codes
                error_message = response_json.get("error", {}).get(
                    "message", "Unknown API error"
                )
                
                if response.status == 401:
                    raise AuthenticationError(
                        f"Authentication failed: {error_message}"
                    )
                elif response.status == 400:
                    raise ValidationError(f"Invalid request: {error_message}")
                elif response.status == 429:
                    retry_after = response.headers.get(
                        "Retry-After", retry_delay
                    )
                    try:
                        retry_after = float(retry_after)
                    except ValueError:
                        retry_after = retry_delay
                    
                    raise RateLimitError(
                        f"Rate limit exceeded: {error_message}",
                        retry_after=retry_after,
                    )
                else:
                    raise DeepSentinelError(
                        f"API error {response.status}: {error_message}"
                    )
            
        except aiohttp.ClientError as e:
            if retry_count < max_retries:
                # Exponential backoff
                backoff_delay = retry_delay * (2 ** retry_count)
                
                self.logger.warning(
                    "Connection error, retrying",
                    error=str(e),
                    retry_count=retry_count,
                    backoff_delay=backoff_delay,
                )
                
                await asyncio.sleep(backoff_delay)
                return await self.request(
                    method,
                    path,
                    data=data,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                    retry_count=retry_count + 1,
                )
            
            raise DeepSentinelError(f"API connection failed: {str(e)}") from e
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a GET request.
        
        Args:
            path: API path
            params: URL parameters
            **kwargs: Additional request parameters
            
        Returns:
            API response
        """
        return await self.request("GET", path, params=params, **kwargs)
    
    async def post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a POST request.
        
        Args:
            path: API path
            data: Request data
            **kwargs: Additional request parameters
            
        Returns:
            API response
        """
        return await self.request("POST", path, data=data, **kwargs)
    
    async def put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a PUT request.
        
        Args:
            path: API path
            data: Request data
            **kwargs: Additional request parameters
            
        Returns:
            API response
        """
        return await self.request("PUT", path, data=data, **kwargs)
    
    async def delete(
        self,
        path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a DELETE request.
        
        Args:
            path: API path
            **kwargs: Additional request parameters
            
        Returns:
            API response
        """
        return await self.request("DELETE", path, **kwargs)
    
    async def verify_credentials(self) -> bool:
        """Verify API credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            await self.get("auth/verify")
            return True
        except (AuthenticationError, DeepSentinelError):
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API service health.
        
        Returns:
            Health check results
        """
        try:
            return await self.get("health")
        except Exception as e:
            self.logger.error("API health check failed", error=str(e))
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def __aenter__(self) -> "DeepSentinelAPIClient":
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.close()