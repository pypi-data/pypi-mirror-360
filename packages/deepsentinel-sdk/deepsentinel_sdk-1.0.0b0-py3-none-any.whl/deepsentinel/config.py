"""DeepSentinel SDK configuration management.

This module provides configuration classes and utilities for managing
DeepSentinel SDK settings, compliance policies, and provider configurations.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from .types import (
    ComplianceAction,
    ProviderConfig,
    ProviderType,
    SeverityLevel,
)


class CompliancePolicy(BaseModel):
    """Configuration for compliance policies and rules.
    
    Attributes:
        name: Name of the policy
        enabled: Whether the policy is enabled
        action: Default action to take on violations
        severity: Default severity level for violations
        rules: Dictionary of rule configurations
        exceptions: List of exceptions to the policy
        custom_handlers: Custom handler configurations
    """
    
    name: str
    enabled: bool = True
    action: ComplianceAction = ComplianceAction.WARN
    severity: SeverityLevel = SeverityLevel.MEDIUM
    rules: Dict[str, Any] = Field(default_factory=dict)
    exceptions: List[str] = Field(default_factory=list)
    custom_handlers: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate policy name is not empty."""
        if not v.strip():
            raise ValueError("Policy name cannot be empty")
        return v.strip()


class PIIPolicy(CompliancePolicy):
    """PII detection and handling policy.
    
    Attributes:
        detection_threshold: Confidence threshold for PII detection
        redaction_strategy: Strategy for redacting PII
        pii_types: Specific PII types to detect
        allow_partial_redaction: Whether to allow partial redaction
    """
    
    detection_threshold: float = Field(0.8, ge=0.0, le=1.0)
    redaction_strategy: str = "mask"
    pii_types: List[str] = Field(
        default_factory=lambda: [
            "email", "phone", "ssn", "credit_card", "ip_address"
        ]
    )
    allow_partial_redaction: bool = True
    
    def __init__(self, **data: Any) -> None:
        """Initialize PII policy with default name."""
        if "name" not in data:
            data["name"] = "pii_detection"
        super().__init__(**data)


class ContentFilterPolicy(CompliancePolicy):
    """Content filtering policy for harmful or inappropriate content.
    
    Attributes:
        filter_categories: Categories of content to filter
        strictness_level: Strictness level for filtering
        custom_patterns: Custom regex patterns to match
        whitelist_patterns: Patterns to whitelist
        context_aware: Whether to consider context in filtering
    """
    
    filter_categories: List[str] = Field(
        default_factory=lambda: ["hate", "violence", "sexual", "harassment"]
    )
    strictness_level: str = "medium"
    custom_patterns: List[str] = Field(default_factory=list)
    whitelist_patterns: List[str] = Field(default_factory=list)
    context_aware: bool = True
    
    def __init__(self, **data: Any) -> None:
        """Initialize content filter policy with default name."""
        if "name" not in data:
            data["name"] = "content_filter"
        super().__init__(**data)


class AuditConfig(BaseModel):
    """Configuration for audit logging and compliance tracking.
    
    Attributes:
        enabled: Whether audit logging is enabled
        log_level: Minimum log level to record
        storage_backend: Storage backend for audit logs
        retention_days: Number of days to retain audit logs
        include_request_body: Whether to log request bodies
        include_response_body: Whether to log response bodies
        exclude_patterns: Patterns to exclude from logging
        encryption_enabled: Whether to encrypt audit logs
        storage_config: Storage backend configuration
    """
    
    enabled: bool = True
    log_level: str = "INFO"
    storage_backend: str = "file"
    retention_days: int = 90
    include_request_body: bool = True
    include_response_body: bool = True
    exclude_patterns: List[str] = Field(default_factory=list)
    encryption_enabled: bool = False
    storage_config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("retention_days")
    def validate_retention_days(cls, v: int) -> int:
        """Validate retention days is positive."""
        if v <= 0:
            raise ValueError("Retention days must be positive")
        return v


class LoggingConfig(BaseModel):
    """Configuration for structured logging.
    
    Attributes:
        level: Log level
        format: Log format
        handlers: Log handlers configuration
        disable_existing_loggers: Whether to disable existing loggers
        structured: Whether to use structured logging
        include_timestamp: Whether to include timestamps
        include_trace_id: Whether to include trace IDs
    """
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers: Dict[str, Any] = Field(default_factory=dict)
    disable_existing_loggers: bool = False
    structured: bool = True
    include_timestamp: bool = True
    include_trace_id: bool = True


class PerformanceConfig(BaseModel):
    """Configuration for performance optimizations.
    
    Attributes:
        enable_caching: Whether to enable response caching
        cache_ttl: Default cache TTL in seconds
        cache_max_size: Maximum cache size
        connection_pool_size: HTTP connection pool size
        connection_pool_per_host: Connections per host
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
        enable_metrics: Whether to collect performance metrics
        metrics_window_size: Size of metrics rolling window
        pattern_cache_size: Size of pattern compilation cache
    """
    
    enable_caching: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    connection_pool_size: int = 100
    connection_pool_per_host: int = 20
    connect_timeout: int = 10
    read_timeout: int = 30
    enable_metrics: bool = True
    metrics_window_size: int = 1000
    pattern_cache_size: int = 1000
    
    @validator("cache_ttl")
    def validate_cache_ttl(cls, v: int) -> int:
        """Validate cache TTL is positive."""
        if v <= 0:
            raise ValueError("Cache TTL must be positive")
        return v
    
    @validator("cache_max_size")
    def validate_cache_max_size(cls, v: int) -> int:
        """Validate cache max size is positive."""
        if v <= 0:
            raise ValueError("Cache max size must be positive")
        return v
    
    @validator("connection_pool_size")
    def validate_connection_pool_size(cls, v: int) -> int:
        """Validate connection pool size is positive."""
        if v <= 0:
            raise ValueError("Connection pool size must be positive")
        return v


class SentinelConfig(BaseModel):
    """Main configuration class for the DeepSentinel SDK.
    
    This class manages all configuration aspects of the SDK including
    provider settings, compliance policies, audit configuration, and
    operational parameters.
    
    Attributes:
        providers: Dictionary of provider configurations
        default_provider: Default provider to use
        compliance_policies: List of compliance policies
        audit_config: Audit logging configuration
        logging_config: Structured logging configuration
        enable_streaming: Whether to enable response streaming
        enable_caching: Whether to enable response caching
        cache_ttl: Cache time-to-live in seconds
        timeout: Default request timeout in seconds
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        debug_mode: Whether debug mode is enabled
        telemetry_enabled: Whether to send telemetry data
        user_agent: Custom user agent string
        environment: Environment name (dev, staging, prod)
    """
    
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)
    default_provider: Optional[str] = None
    compliance_policies: List[CompliancePolicy] = Field(default_factory=list)
    audit_config: AuditConfig = Field(default_factory=AuditConfig)
    logging_config: LoggingConfig = Field(default_factory=LoggingConfig)
    enable_streaming: bool = False
    performance_config: PerformanceConfig = Field(
        default_factory=PerformanceConfig
    )
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    debug_mode: bool = False
    telemetry_enabled: bool = True
    user_agent: Optional[str] = None
    environment: str = "production"
    
    class Config:
        """Pydantic configuration."""
        
        extra = "forbid"
        validate_assignment = True
    
    def __init__(self, **data: Any) -> None:
        """Initialize configuration with environment variables."""
        # Load from environment variables
        env_data = self._load_from_env()
        env_data.update(data)
        super().__init__(**env_data)
    
    @validator("default_provider")
    def validate_default_provider(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Optional[str]:
        """Validate default provider exists in providers dict."""
        if v and "providers" in values and v not in values["providers"]:
            raise ValueError(f"Default provider '{v}' not found in providers")
        return v
    
    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Returns:
            Dictionary of configuration values from environment variables.
        """
        env_config: Dict[str, Any] = {}
        
        # Basic configuration
        if debug := os.getenv("DEEPSENTINEL_DEBUG"):
            env_config["debug_mode"] = debug.lower() in ("true", "1", "yes")
        
        if env := os.getenv("DEEPSENTINEL_ENVIRONMENT"):
            env_config["environment"] = env
        
        if timeout := os.getenv("DEEPSENTINEL_TIMEOUT"):
            try:
                env_config["timeout"] = int(timeout)
            except ValueError:
                pass
        
        if retries := os.getenv("DEEPSENTINEL_MAX_RETRIES"):
            try:
                env_config["max_retries"] = int(retries)
            except ValueError:
                pass
        
        # Provider configurations
        providers = {}
        
        # OpenAI configuration
        if openai_key := os.getenv("OPENAI_API_KEY"):
            providers["openai"] = ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key=openai_key,
                base_url=os.getenv("OPENAI_BASE_URL"),
            )
        
        # Anthropic configuration
        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            providers["anthropic"] = ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                api_key=anthropic_key,
                base_url=os.getenv("ANTHROPIC_BASE_URL"),
            )
        
        # Azure OpenAI configuration
        if azure_key := os.getenv("AZURE_OPENAI_API_KEY"):
            providers["azure_openai"] = ProviderConfig(
                provider_type=ProviderType.AZURE_OPENAI,
                api_key=azure_key,
                base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
                extra_config={
                    "api_version": os.getenv(
                        "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"
                    )
                },
            )
        
        if providers:
            env_config["providers"] = providers
            # Set default provider if only one is configured
            if len(providers) == 1:
                env_config["default_provider"] = list(providers.keys())[0]
            elif default := os.getenv("DEEPSENTINEL_DEFAULT_PROVIDER"):
                env_config["default_provider"] = default
        
        return env_config
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "SentinelConfig":
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            SentinelConfig instance loaded from the file
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the configuration file format is invalid
        """
        import json
        import yaml
        
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )
        
        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yml", ".yaml"]:
                config_data = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                config_data = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported configuration file format: "
                    f"{config_path.suffix}"
                )
        
        return cls(**config_data)
    
    def add_provider(
        self,
        name: str,
        provider_config: ProviderConfig,
        set_as_default: bool = False,
    ) -> None:
        """Add a new provider configuration.
        
        Args:
            name: Name of the provider
            provider_config: Provider configuration
            set_as_default: Whether to set as the default provider
        """
        self.providers[name] = provider_config
        if set_as_default or not self.default_provider:
            self.default_provider = name
    
    def add_compliance_policy(self, policy: CompliancePolicy) -> None:
        """Add a compliance policy.
        
        Args:
            policy: Compliance policy to add
        """
        # Remove existing policy with the same name
        self.compliance_policies = [
            p for p in self.compliance_policies if p.name != policy.name
        ]
        self.compliance_policies.append(policy)
    
    def get_provider_config(
        self, provider_name: Optional[str] = None
    ) -> ProviderConfig:
        """Get provider configuration by name.
        
        Args:
            provider_name: Name of the provider (uses default if None)
            
        Returns:
            Provider configuration
            
        Raises:
            ValueError: If provider is not found
        """
        name = provider_name or self.default_provider
        if not name:
            raise ValueError(
                "No provider specified and no default provider set"
            )
        
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not found in configuration")
        
        return self.providers[name]
    
    def get_compliance_policy(
        self, policy_name: str
    ) -> Optional[CompliancePolicy]:
        """Get compliance policy by name.
        
        Args:
            policy_name: Name of the policy
            
        Returns:
            Compliance policy if found, None otherwise
        """
        for policy in self.compliance_policies:
            if policy.name == policy_name:
                return policy
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return self.dict()
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration updates
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)