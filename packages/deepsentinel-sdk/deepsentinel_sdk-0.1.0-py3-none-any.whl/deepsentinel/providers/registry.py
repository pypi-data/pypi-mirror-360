"""Provider registry for managing LLM provider instances.

This module provides a centralized registry for managing different LLM
provider adapters, including registration, lookup, and lifecycle management.
"""

import asyncio
from typing import Any, Dict, List, Optional, Type

from ..config import ProviderConfig, SentinelConfig
from ..exceptions import ConfigurationError
from .base import ProviderAdapter


class ProviderRegistry:
    """Registry for managing LLM provider instances.
    
    This class provides centralized management of provider adapters,
    including registration, initialization, and lookup operations.
    
    Attributes:
        _providers: Dictionary of registered provider instances
        _provider_classes: Dictionary of available provider classes
        _default_provider: Default provider name
    """
    
    def __init__(self) -> None:
        """Initialize the provider registry."""
        self._providers: Dict[str, ProviderAdapter] = {}
        self._provider_classes: Dict[str, Type[ProviderAdapter]] = {}
        self._default_provider: Optional[str] = None
        self._initialized = False
    
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
    ) -> None:
        """Register a provider class.
        
        Args:
            provider_type: Type identifier for the provider
            provider_class: Provider class to register
            
        Raises:
            ValueError: If provider type is already registered
        """
        if provider_type in self._provider_classes:
            raise ValueError(
                f"Provider type '{provider_type}' already registered"
            )
        
        if not issubclass(provider_class, ProviderAdapter):
            raise ValueError(
                "Provider class must inherit from ProviderAdapter"
            )
        
        self._provider_classes[provider_type] = provider_class
    
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
    
    def get_provider(self, name: Optional[str] = None) -> ProviderAdapter:
        """Get a provider by name.
        
        Args:
            name: Provider name (uses default if None)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider is not found
        """
        provider_name = name or self._default_provider
        
        if not provider_name:
            raise ValueError(
                "No provider specified and no default provider set"
            )
        
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        return self._providers[provider_name]
    
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
        registry = cls()
        
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
    """Initialize default provider classes in the global registry."""
    # Import and register default providers
    try:
        from .openai import OpenAIProvider
        from .anthropic import AnthropicProvider
        # from .azure_openai import AzureOpenAIProvider (Not yet implemented)
        
        registry = get_global_registry()
        registry.register_provider_class("openai", OpenAIProvider)
        registry.register_provider_class("anthropic", AnthropicProvider)
        # registry.register_provider_class("azure_openai", AzureOpenAIProvider)
    except ImportError as e:
        # Log import errors but don't crash
        import logging
        logging.warning(f"Error registering providers: {e}")