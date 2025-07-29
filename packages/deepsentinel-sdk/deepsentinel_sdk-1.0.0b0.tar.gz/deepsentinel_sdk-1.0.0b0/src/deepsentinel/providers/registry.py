"""Provider registry for managing LLM provider instances.

This module provides a centralized registry for managing different LLM
provider adapters, including registration, lookup, and lifecycle management.
"""

import asyncio
import logging
import threading
from typing import Any, Dict, List, Optional, Type

from ..config import ProviderConfig, SentinelConfig
from ..exceptions import ConfigurationError
from .base import ProviderAdapter

# Configure logging
logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for managing LLM provider instances.
    
    This class provides centralized management of provider adapters,
    including registration, initialization, lookup operations, model mapping,
    and failover capabilities with thread-safe operations.
    
    Attributes:
        _providers: Dictionary of registered provider instances
        _provider_classes: Dictionary of available provider classes
        _default_provider: Default provider name
        _model_mapping: Mapping from model names to provider names
        _provider_metadata: Metadata and capabilities for each provider
        _failover_chains: Failover chains for providers
        _health_status: Health status cache for providers
    """
    
    def __init__(self) -> None:
        """Initialize the provider registry."""
        self._providers: Dict[str, ProviderAdapter] = {}
        self._provider_classes: Dict[str, Type[ProviderAdapter]] = {}
        self._default_provider: Optional[str] = None
        self._initialized = False
        
        # Model mapping and metadata
        self._model_mapping: Dict[str, str] = {}
        self._provider_metadata: Dict[str, Dict[str, Any]] = {}
        self._failover_chains: Dict[str, List[str]] = {}
        
        # Health monitoring
        self._health_status: Dict[str, Dict[str, Any]] = {}
        self._last_health_check: Dict[str, float] = {}
        self._health_check_interval = 300  # 5 minutes
        
        # Thread safety
        self._lock = asyncio.Lock()
        self._thread_lock = threading.RLock()
    
    @property
    def providers(self) -> Dict[str, ProviderAdapter]:
        """Get all registered providers."""
        return self._providers.copy()
    
    @property
    def provider_names(self) -> List[str]:
        """Get list of registered provider names."""
        return list(self._providers.keys())
    
    @property
    def default_provider(self) -> Optional[str]:
        """Get the default provider name."""
        return self._default_provider
    
    @property
    def is_initialized(self) -> bool:
        """Check if the registry is initialized."""
        return self._initialized
    
    def register_provider_class(
        self,
        provider_type: str,
        provider_class: Type[ProviderAdapter],
        supported_models: Optional[List[str]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a provider class with metadata.
        
        Args:
            provider_type: Type identifier for the provider
            provider_class: Provider class to register
            supported_models: List of models supported by this provider
            capabilities: Dictionary of provider capabilities
            
        Raises:
            ValueError: If provider type is already registered
        """
        with self._thread_lock:
            if provider_type in self._provider_classes:
                raise ValueError(
                    f"Provider type '{provider_type}' already registered"
                )
            
            if not issubclass(provider_class, ProviderAdapter):
                raise ValueError(
                    "Provider class must inherit from ProviderAdapter"
                )
            
            self._provider_classes[provider_type] = provider_class
            
            # Store provider metadata
            try:
                registered_time = (
                    asyncio.get_event_loop().time()
                    if asyncio.get_event_loop().is_running()
                    else 0
                )
            except RuntimeError:
                registered_time = 0
                
            metadata = {
                "provider_type": provider_type,
                "supported_models": supported_models or [],
                "capabilities": capabilities or {},
                "registered_at": registered_time,
            }
            self._provider_metadata[provider_type] = metadata
            
            logger.info(
                f"Registered provider class '{provider_type}' with "
                f"{len(supported_models or [])} supported models"
            )
    
    def register_model_mapping(
        self, model_name: str, provider_name: str
    ) -> None:
        """Register a mapping from model name to provider.
        
        Args:
            model_name: Name of the model
            provider_name: Name of the provider that supports this model
        """
        with self._thread_lock:
            self._model_mapping[model_name] = provider_name
            logger.debug(
                f"Mapped model '{model_name}' to provider '{provider_name}'"
            )
    
    def register_model_mappings(
        self, mappings: Dict[str, str]
    ) -> None:
        """Register multiple model mappings at once.
        
        Args:
            mappings: Dictionary mapping model names to provider names
        """
        with self._thread_lock:
            self._model_mapping.update(mappings)
            logger.info(f"Registered {len(mappings)} model mappings")
    
    def get_provider_for_model(self, model_name: str) -> Optional[str]:
        """Get the provider name that supports a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Provider name if found, None otherwise
        """
        with self._thread_lock:
            return self._model_mapping.get(model_name)
    
    def get_models_for_provider(self, provider_name: str) -> List[str]:
        """Get all models supported by a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of model names supported by the provider
        """
        with self._thread_lock:
            return [
                model for model, provider in self._model_mapping.items()
                if provider == provider_name
            ]
    
    def get_provider_metadata(
        self, provider_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get metadata for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider metadata if found, None otherwise
        """
        with self._thread_lock:
            # First try to get from registered providers
            if provider_name in self._providers:
                provider = self._providers[provider_name]
                provider_type = provider.provider_type.value
                return self._provider_metadata.get(provider_type)
            
            # Then try direct lookup by provider type
            return self._provider_metadata.get(provider_name)
    
    def set_failover_chain(
        self, primary_provider: str, fallback_providers: List[str]
    ) -> None:
        """Set up a failover chain for a provider.
        
        Args:
            primary_provider: Name of the primary provider
            fallback_providers: List of fallback provider names in order
        """
        with self._thread_lock:
            self._failover_chains[primary_provider] = fallback_providers.copy()
            logger.info(
                f"Set failover chain for '{primary_provider}': "
                f"{' -> '.join(fallback_providers)}"
            )
    
    def get_failover_chain(self, provider_name: str) -> List[str]:
        """Get the failover chain for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            List of fallback provider names
        """
        with self._thread_lock:
            return self._failover_chains.get(provider_name, []).copy()
    
    def create_provider(
        self,
        name: str,
        config: ProviderConfig,
    ) -> ProviderAdapter:
        """Create a provider instance from configuration.
        
        Args:
            name: Name for the provider instance
            config: Provider configuration
            
        Returns:
            Created provider instance
            
        Raises:
            ConfigurationError: If provider type is not supported
        """
        provider_type = config.provider_type.value
        
        if provider_type not in self._provider_classes:
            raise ConfigurationError(
                f"Unsupported provider type: {provider_type}",
                config_key="provider_type",
                config_value=provider_type,
            )
        
        provider_class = self._provider_classes[provider_type]
        return provider_class(config, name)
    
    async def register_provider(
        self,
        name: str,
        config: ProviderConfig,
        initialize: bool = True,
        set_as_default: bool = False,
    ) -> ProviderAdapter:
        """Register a new provider instance.
        
        Args:
            name: Name for the provider instance
            config: Provider configuration
            initialize: Whether to initialize the provider immediately
            set_as_default: Whether to set as the default provider
            
        Returns:
            Registered provider instance
            
        Raises:
            ValueError: If provider name already exists
            ConfigurationError: If configuration is invalid
            ProviderError: If initialization fails
        """
        if name in self._providers:
            raise ValueError(f"Provider '{name}' already registered")
        
        provider = self.create_provider(name, config)
        
        if initialize:
            await provider.initialize()
        
        self._providers[name] = provider
        
        if set_as_default or not self._default_provider:
            self._default_provider = name
        
        return provider
    
    def unregister_provider(self, name: str) -> None:
        """Unregister a provider.
        
        Args:
            name: Name of the provider to unregister
            
        Raises:
            ValueError: If provider is not found
        """
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not found")
        
        provider = self._providers.pop(name)
        
        # Clean up the provider
        if provider.is_initialized:
            asyncio.create_task(provider.cleanup())
        
        # Update default provider if necessary
        if self._default_provider == name:
            self._default_provider = (
                list(self._providers.keys())[0] if self._providers else None
            )
    
    def get_provider(
        self,
        name: Optional[str] = None,
        model: Optional[str] = None,
        use_failover: bool = True,
    ) -> ProviderAdapter:
        """Get a provider by name or model with failover support.
        
        Args:
            name: Provider name (uses default if None)
            model: Model name to get appropriate provider for
            use_failover: Whether to use failover if primary provider fails
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If no suitable provider is found
        """
        # Determine provider name from model if not specified
        if not name and model:
            name = self.get_provider_for_model(model)
        
        provider_name = name or self._default_provider
        
        if not provider_name:
            raise ValueError(
                "No provider specified and no default provider set"
            )
        
        # Try primary provider first
        if provider_name in self._providers:
            provider = self._providers[provider_name]
            if self._is_provider_healthy(provider_name) or not use_failover:
                return provider
        
        # Try failover chain if primary provider is unhealthy
        if use_failover:
            failover_chain = self.get_failover_chain(provider_name)
            for fallback_name in failover_chain:
                if (fallback_name in self._providers and
                        self._is_provider_healthy(fallback_name)):
                    logger.warning(
                        f"Using failover provider '{fallback_name}' "
                        f"instead of '{provider_name}'"
                    )
                    return self._providers[fallback_name]
        
        # If we reach here, either provider not found or all providers
        # unhealthy
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        else:
            # Return the original provider even if unhealthy
            logger.warning(
                f"Returning potentially unhealthy provider '{provider_name}'"
            )
            return self._providers[provider_name]
    
    def get_provider_with_model_support(
        self, model: str, use_failover: bool = True
    ) -> ProviderAdapter:
        """Get a provider that supports the specified model.
        
        Args:
            model: Model name to find provider for
            use_failover: Whether to use failover providers
            
        Returns:
            Provider instance that supports the model
            
        Raises:
            ValueError: If no provider supports the model
        """
        # First try direct model mapping
        provider_name = self.get_provider_for_model(model)
        if provider_name:
            return self.get_provider(
                name=provider_name,
                model=model,
                use_failover=use_failover
            )
        
        # Fall back to checking all providers for model support
        for name, provider in self._providers.items():
            try:
                # Check if provider has models list
                models = asyncio.run(provider.list_models())
                model_ids = [m.get("id", "") for m in models]
                if model in model_ids:
                    # Auto-register this mapping for future use
                    self.register_model_mapping(model, name)
                    return self.get_provider(
                        name=name,
                        use_failover=use_failover
                    )
            except Exception as e:
                logger.debug(
                    f"Failed to check models for provider '{name}': {e}"
                )
                continue
        
        raise ValueError(
            f"No provider found that supports model '{model}'"
        )
    
    def _is_provider_healthy(self, provider_name: str) -> bool:
        """Check if a provider is healthy using cached health status.
        
        Args:
            provider_name: Name of the provider to check
            
        Returns:
            True if provider is healthy, False otherwise
        """
        if provider_name not in self._providers:
            return False
        
        # Check if we have recent health status
        current_time = asyncio.get_event_loop().time()
        last_check = self._last_health_check.get(provider_name, 0)
        
        if current_time - last_check < self._health_check_interval:
            # Use cached status
            status = self._health_status.get(provider_name, {})
            return status.get("status") == "healthy"
        
        # Need fresh health check
        try:
            provider = self._providers[provider_name]
            if not provider.is_initialized:
                return False
            
            # Perform health check asynchronously
            health_result = asyncio.create_task(provider.health_check())
            # Don't wait for the result, assume healthy for now
            # and update cache when result is available

            def update_health_cache(task):
                try:
                    result = task.result()
                    self._health_status[provider_name] = result
                    self._last_health_check[provider_name] = current_time
                except Exception:
                    self._health_status[provider_name] = {
                        "status": "unhealthy",
                        "error": "Health check failed"
                    }
                    self._last_health_check[provider_name] = current_time
            
            health_result.add_done_callback(update_health_cache)
            
            # Return current cached status or assume healthy
            status = self._health_status.get(
                provider_name, {"status": "healthy"}
            )
            return status.get("status") == "healthy"
            
        except Exception:
            return False
    
    def has_provider(self, name: str) -> bool:
        """Check if a provider is registered.
        
        Args:
            name: Provider name to check
            
        Returns:
            True if provider is registered, False otherwise
        """
        return name in self._providers
    
    def set_default_provider(self, name: str) -> None:
        """Set the default provider.
        
        Args:
            name: Name of the provider to set as default
            
        Raises:
            ValueError: If provider is not found
        """
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not found")
        
        self._default_provider = name
    
    async def initialize_all(self) -> None:
        """Initialize all registered providers."""
        if self._initialized:
            return
        
        initialization_tasks = []
        for provider in self._providers.values():
            if not provider.is_initialized:
                initialization_tasks.append(provider.initialize())
        
        if initialization_tasks:
            await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        self._initialized = True
    
    async def cleanup_all(self) -> None:
        """Clean up all providers."""
        cleanup_tasks = []
        for provider in self._providers.values():
            if provider.is_initialized:
                cleanup_tasks.append(provider.cleanup())
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self._initialized = False
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health checks on all providers.
        
        Returns:
            Dictionary mapping provider names to health check results
        """
        results = {}
        
        for name, provider in self._providers.items():
            try:
                if provider.is_initialized:
                    results[name] = await provider.health_check()
                else:
                    results[name] = {
                        "status": "not_initialized",
                        "error": "Provider not initialized",
                    }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                }
        
        return results
    
    @classmethod
    async def from_config(cls, config: SentinelConfig) -> "ProviderRegistry":
        """Create a provider registry from configuration.
        
        Args:
            config: Sentinel configuration containing provider configs
            
        Returns:
            Configured provider registry
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Initialize default provider classes first
        await initialize_default_providers()
        
        registry = cls()
        
        # Copy provider classes from global registry
        global_registry = get_global_registry()
        registry._provider_classes = global_registry._provider_classes.copy()
        registry._model_mapping = global_registry._model_mapping.copy()
        registry._provider_metadata = global_registry._provider_metadata.copy()
        
        # Register providers from configuration
        for name, provider_config in config.providers.items():
            try:
                await registry.register_provider(
                    name=name,
                    config=provider_config,
                    initialize=True,
                    set_as_default=name == config.default_provider,
                )
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to register provider '{name}': {str(e)}",
                    config_key=f"providers.{name}",
                ) from e
        
        return registry
    
    async def __aenter__(self) -> "ProviderRegistry":
        """Async context manager entry."""
        await self.initialize_all()
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.cleanup_all()
    
    def __len__(self) -> int:
        """Return the number of registered providers."""
        return len(self._providers)
    
    def __contains__(self, name: str) -> bool:
        """Check if a provider is registered."""
        return name in self._providers
    
    def __iter__(self):
        """Iterate over provider names."""
        return iter(self._providers)
    
    def __repr__(self) -> str:
        """Return string representation of the registry."""
        return (
            f"ProviderRegistry("
            f"providers={len(self._providers)}, "
            f"default='{self._default_provider}', "
            f"initialized={self._initialized})"
        )


# Global registry instance
_global_registry: Optional[ProviderRegistry] = None


def get_global_registry() -> ProviderRegistry:
    """Get the global provider registry instance.
    
    Returns:
        Global provider registry
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry


def set_global_registry(registry: ProviderRegistry) -> None:
    """Set the global provider registry instance.
    
    Args:
        registry: Provider registry to set as global
    """
    global _global_registry
    _global_registry = registry


async def initialize_default_providers() -> None:
    """Initialize default provider classes with model mappings."""
    registry = get_global_registry()
    
    # Import and register OpenAI provider
    try:
        from .openai import OpenAIProvider
        
        openai_models = [
            "gpt-4", "gpt-4-0314", "gpt-4-0613",
            "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613",
            "gpt-4-1106-preview", "gpt-4-vision-preview",
            "gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613",
            "gpt-3.5-turbo-1106",
            "text-davinci-003", "text-davinci-002",
            "text-embedding-ada-002", "text-embedding-3-small",
            "text-embedding-3-large",
            "whisper-1", "dall-e-2", "dall-e-3"
        ]
        
        openai_capabilities = {
            "supports_chat": True,
            "supports_completion": True,
            "supports_embeddings": True,
            "supports_audio": True,
            "supports_images": True,
            "supports_streaming": True,
            "supports_functions": True,
            "supports_tools": True,
        }
        
        registry.register_provider_class(
            "openai",
            OpenAIProvider,
            supported_models=openai_models,
            capabilities=openai_capabilities
        )
        
        # Register OpenAI model mappings
        openai_mappings = {model: "openai" for model in openai_models}
        registry.register_model_mappings(openai_mappings)
        
        logger.info("Registered OpenAI provider with model mappings")
        
    except ImportError as e:
        logger.warning(f"Failed to import OpenAI provider: {e}")
    
    # Import and register Anthropic provider
    try:
        from .anthropic import AnthropicProvider
        
        anthropic_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
            "claude-instant-1"
        ]
        
        anthropic_capabilities = {
            "supports_chat": True,
            "supports_completion": True,  # Emulated via chat
            "supports_embeddings": False,
            "supports_audio": False,
            "supports_images": False,
            "supports_streaming": True,
            "supports_functions": True,  # Limited support
            "supports_tools": True,
        }
        
        registry.register_provider_class(
            "anthropic",
            AnthropicProvider,
            supported_models=anthropic_models,
            capabilities=anthropic_capabilities
        )
        
        # Register Anthropic model mappings
        anthropic_mappings = {model: "anthropic" for model in anthropic_models}
        registry.register_model_mappings(anthropic_mappings)
        
        logger.info("Registered Anthropic provider with model mappings")
        
    except ImportError as e:
        logger.warning(f"Failed to import Anthropic provider: {e}")
    
    logger.info(
        f"Provider registry initialized with "
        f"{len(registry._provider_classes)} provider classes and "
        f"{len(registry._model_mapping)} model mappings"
    )


def setup_default_failover_chains(registry: ProviderRegistry) -> None:
    """Set up default failover chains for common scenarios.
    
    Args:
        registry: Provider registry to configure failover chains for
    """
    # Set up failover chains based on common use cases
    
    # For general chat completions: OpenAI -> Anthropic
    if registry.has_provider("openai") and registry.has_provider("anthropic"):
        registry.set_failover_chain("openai", ["anthropic"])
        registry.set_failover_chain("anthropic", ["openai"])
        logger.info(
            "Set up bidirectional failover between OpenAI and Anthropic"
        )
    
    # For embeddings: Only OpenAI supports embeddings currently
    if registry.has_provider("openai"):
        registry.set_failover_chain("openai", [])  # No fallback for embeddings
        logger.info("Set up OpenAI as primary for embeddings (no fallback)")


async def create_registry_from_config(
    config: SentinelConfig,
    setup_failover: bool = True,
) -> ProviderRegistry:
    """Create and configure a provider registry from SentinelConfig.
    
    Args:
        config: Sentinel configuration
        setup_failover: Whether to set up default failover chains
        
    Returns:
        Configured provider registry
    """
    # Create registry from config (initialize_default_providers is called 
    # in from_config)
    registry = await ProviderRegistry.from_config(config)
    
    # Set up failover chains if requested
    if setup_failover:
        setup_default_failover_chains(registry)
    
    return registry