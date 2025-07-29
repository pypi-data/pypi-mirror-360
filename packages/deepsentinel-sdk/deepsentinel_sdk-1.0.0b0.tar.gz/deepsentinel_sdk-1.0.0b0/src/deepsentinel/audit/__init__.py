"""Audit logging and event tracking components.

This module provides a comprehensive audit system for tracking operations,
compliance checks, and performance metrics throughout the SDK.
"""

from .client import (
    AuditClient,
    AuditStorage,
    FileAuditStorage, 
    APIAuditStorage,
    DatabaseAuditStorage,
)
from .events import (
    AuditEvent,
    AuditEventType,
    ChatOperationEvent,
    CompletionOperationEvent,
    ComplianceViolationEvent,
    ConfigurationChangeEvent,
    EmbeddingOperationEvent,
    OperationMetrics,
    PerformanceMetricsEvent,
    SystemErrorEvent,
    create_chat_request_event,
    create_chat_response_event,
    create_compliance_violation_event,
    create_performance_metrics_event,
    create_system_error_event,
)

__all__ = [
    # Client classes
    "AuditClient",
    "AuditStorage",
    "FileAuditStorage", 
    "APIAuditStorage",
    "DatabaseAuditStorage",
    
    # Event classes
    "AuditEvent",
    "AuditEventType",
    "ChatOperationEvent",
    "CompletionOperationEvent",
    "ComplianceViolationEvent",
    "ConfigurationChangeEvent",
    "EmbeddingOperationEvent",
    "OperationMetrics",
    "PerformanceMetricsEvent",
    "SystemErrorEvent",
    
    # Event creation helpers
    "create_chat_request_event",
    "create_chat_response_event",
    "create_compliance_violation_event",
    "create_performance_metrics_event",
    "create_system_error_event",
]