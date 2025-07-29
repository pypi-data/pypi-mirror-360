"""DeepSentinel SDK - AI compliance middleware for safe LLM interactions.

This package provides a middleware layer between applications and LLM
providers, with comprehensive compliance checks, audit logging, and performance
optimizations for AI safety and compliance.
"""

__version__ = "1.0.0-beta"

from .api.audit import AuditAPI
from .api.client import DeepSentinelAPIClient
from .api.compliance import ComplianceAPI
from .client import SentinelClient
from .compliance.engine import ComplianceEngine
from .compliance.interceptor import ComplianceInterceptor
from .compliance.policies import PolicyManager
from .compliance.detection.engine import DetectionEngine
from .compliance.detection.patterns import PatternMatcher
from .compliance.detection.pii import PIIDetector
from .compliance.detection.phi import PHIDetector
from .compliance.detection.pci import PCIDetector
from .cache.client import CacheClient, CacheEntry, CacheStats
from .config import (
    AuditConfig,
    CompliancePolicy,
    ContentFilterPolicy,
    LoggingConfig,
    PerformanceConfig,
    PIIPolicy,
    ProviderConfig,
    SentinelConfig,
)
from .exceptions import (
    AuthenticationError,
    ComplianceViolationError,
    ConfigurationError,
    DeepSentinelError,
    MCPError,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from .interfaces import (
    AudioInterface,
    ChatInterface,
    CompletionsInterface,
    EmbeddingsInterface,
    ImageInterface,
    ModelsInterface,
)
from .metrics.collector import (
    MetricsCollector,
    PerformanceMetrics,
    TokenUsageMetrics,
)
from .providers.base import BaseLLMProvider, ProviderAdapter
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.registry import ProviderRegistry, get_global_registry
from .types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    Message,
)

__all__ = [
    # Main client
    "SentinelClient",
    # API clients
    "DeepSentinelAPIClient",
    "ComplianceAPI",
    "AuditAPI",
    # Compliance components
    "ComplianceEngine",
    "ComplianceInterceptor",
    "PolicyManager",
    "DetectionEngine",
    "PatternMatcher",
    "PIIDetector",
    "PHIDetector",
    "PCIDetector",
    # Configuration classes
    "SentinelConfig",
    "CompliancePolicy",
    "PIIPolicy",
    "ContentFilterPolicy",
    "AuditConfig",
    "LoggingConfig",
    "PerformanceConfig",
    # Performance components
    "CacheClient",
    "CacheEntry",
    "CacheStats",
    "MetricsCollector",
    "PerformanceMetrics",
    "TokenUsageMetrics",
    # Exception classes
    "DeepSentinelError",
    "ComplianceViolationError",
    "ProviderError",
    "ConfigurationError",
    "MCPError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    # Interface classes
    "ChatInterface",
    "CompletionsInterface",
    "EmbeddingsInterface",
    "ModelsInterface",
    "AudioInterface",
    "ImageInterface",
    # Data types
    "ChatRequest",
    "ChatResponse",
    "CompletionRequest",
    "CompletionResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "Message",
    "ProviderConfig",
    # Provider classes
    "ProviderAdapter",
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "ProviderRegistry",
    "get_global_registry",
]