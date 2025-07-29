"""Audit event types and schemas for DeepSentinel SDK.

This module defines comprehensive audit event types and schemas for tracking
operations, compliance violations, and performance metrics.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator

from ..types import AuditEntry, SeverityLevel


class AuditEventType(str, Enum):
    """Enumeration of audit event types."""
    
    # Operation events
    CHAT_REQUEST = "chat_request"
    CHAT_RESPONSE = "chat_response"
    COMPLETION_REQUEST = "completion_request"
    COMPLETION_RESPONSE = "completion_response"
    EMBEDDING_REQUEST = "embedding_request"
    EMBEDDING_RESPONSE = "embedding_response"
    
    # Compliance events
    COMPLIANCE_CHECK = "compliance_check"
    COMPLIANCE_VIOLATION = "compliance_violation"
    COMPLIANCE_POLICY_UPDATE = "compliance_policy_update"
    
    # Performance events
    LATENCY_REPORT = "latency_report"
    RATE_LIMIT_HIT = "rate_limit_hit"
    TOKEN_USAGE = "token_usage"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    CONFIGURATION_CHANGE = "configuration_change"
    
    # Authentication events
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    
    # Custom events
    CUSTOM = "custom"


class OperationMetrics(BaseModel):
    """Performance metrics for an operation.
    
    Attributes:
        total_duration_ms: Total duration of the operation in milliseconds
        request_duration_ms: Duration of the request phase in milliseconds
        response_duration_ms: Duration of the response phase in milliseconds
        token_count: Number of tokens used
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        tpm: Tokens per minute rate
        rpm: Requests per minute rate
    """
    
    total_duration_ms: Optional[float] = None
    request_duration_ms: Optional[float] = None
    response_duration_ms: Optional[float] = None
    token_count: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    tpm: Optional[float] = None
    rpm: Optional[float] = None


class AuditEvent(BaseModel):
    """Base class for all audit events.
    
    Attributes:
        id: Unique identifier for the event
        event_type: Type of the audit event
        timestamp: When the event occurred
        user_id: Identifier of the user
        session_id: Session identifier
        severity: Severity level of the event
        source: Source of the event (component, module)
        details: Additional event details
        metadata: Additional contextual metadata
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AuditEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.LOW
    source: str = "deepsentinel"
    details: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            **self.model_dump(),
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_audit_entry(self) -> AuditEntry:
        """Convert event to audit entry.
        
        Returns:
            AuditEntry representation of the event
        """
        operation = self.event_type.value
        
        # Extract relevant fields for audit entry
        entry_data = {
            "id": self.id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "operation": operation,
            "metadata": self.metadata,
        }
        
        # Add provider and model if available
        provider = self.details.get("provider")
        if provider:
            entry_data["provider"] = provider
            
        model = self.details.get("model")
        if model:
            entry_data["model"] = model
            
        # Add request/response data if available
        if "request_data" in self.details:
            entry_data["request_data"] = self.details["request_data"]
            
        if "response_data" in self.details:
            entry_data["response_data"] = self.details["response_data"]
            
        # Add compliance checks if available
        if "compliance_checks" in self.details:
            entry_data["compliance_checks"] = self.details["compliance_checks"]
            
        # Add cost and duration if available
        if "cost" in self.details:
            entry_data["cost"] = self.details["cost"]
            
        metrics = self.details.get("metrics", {})
        if metrics and "total_duration_ms" in metrics:
            entry_data["duration_ms"] = metrics["total_duration_ms"]
            
        return AuditEntry(**entry_data)


class ChatOperationEvent(AuditEvent):
    """Audit event for chat operations.
    
    Attributes:
        request_id: Identifier of the request
        model: Model used for the chat
        provider: Provider of the model
        metrics: Performance metrics
        request_data: Request data summary
        response_data: Response data summary
    """
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    provider: str
    metrics: Optional[OperationMetrics] = None
    request_data: Dict[str, Any] = Field(default_factory=dict)
    response_data: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode="after")
    def update_details(self) -> "ChatOperationEvent":
        """Update details with specialized fields."""
        self.details.update({
            "request_id": self.request_id,
            "model": self.model,
            "provider": self.provider,
            "request_data": self.request_data,
            "response_data": self.response_data,
        })
        
        if self.metrics:
            self.details["metrics"] = self.metrics.model_dump()
            
        return self


class CompletionOperationEvent(AuditEvent):
    """Audit event for text completion operations.
    
    Attributes:
        request_id: Identifier of the request
        model: Model used for completion
        provider: Provider of the model
        metrics: Performance metrics
        request_data: Request data summary
        response_data: Response data summary
    """
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    provider: str
    metrics: Optional[OperationMetrics] = None
    request_data: Dict[str, Any] = Field(default_factory=dict)
    response_data: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode="after")
    def update_details(self) -> "CompletionOperationEvent":
        """Update details with specialized fields."""
        self.details.update({
            "request_id": self.request_id,
            "model": self.model,
            "provider": self.provider,
            "request_data": self.request_data,
            "response_data": self.response_data,
        })
        
        if self.metrics:
            self.details["metrics"] = self.metrics.model_dump()
            
        return self


class EmbeddingOperationEvent(AuditEvent):
    """Audit event for embedding operations.
    
    Attributes:
        request_id: Identifier of the request
        model: Model used for embeddings
        provider: Provider of the model
        metrics: Performance metrics
        request_data: Request data summary
        response_data: Response data summary
    """
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    provider: str
    metrics: Optional[OperationMetrics] = None
    request_data: Dict[str, Any] = Field(default_factory=dict)
    response_data: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode="after")
    def update_details(self) -> "EmbeddingOperationEvent":
        """Update details with specialized fields."""
        self.details.update({
            "request_id": self.request_id,
            "model": self.model,
            "provider": self.provider,
            "request_data": self.request_data,
            "response_data": self.response_data,
        })
        
        if self.metrics:
            self.details["metrics"] = self.metrics.model_dump()
            
        return self


class ComplianceViolationEvent(AuditEvent):
    """Audit event for compliance violations.
    
    Attributes:
        policy_name: Name of the violated policy
        violation_type: Type of violation
        severity: Severity level of the violation
        action_taken: Action taken in response to the violation
        violation_details: Details about the violation
        resource_id: Identifier of the resource with violation
    """
    
    policy_name: str
    violation_type: str
    severity: SeverityLevel
    action_taken: str
    violation_details: Dict[str, Any] = Field(default_factory=dict)
    resource_id: Optional[str] = None
    
    @model_validator(mode="after")
    def update_details(self) -> "ComplianceViolationEvent":
        """Update details with specialized fields."""
        self.details.update({
            "policy_name": self.policy_name,
            "violation_type": self.violation_type,
            "action_taken": self.action_taken,
            "violation_details": self.violation_details,
        })
        
        if self.resource_id:
            self.details["resource_id"] = self.resource_id
            
        return self


class PerformanceMetricsEvent(AuditEvent):
    """Audit event for performance metrics.
    
    Attributes:
        operation_type: Type of operation being measured
        metrics: Performance metrics data
        model: Model used for the operation
        provider: Provider of the model
        component: Component being measured
    """
    
    operation_type: str
    metrics: OperationMetrics
    model: Optional[str] = None
    provider: Optional[str] = None
    component: Optional[str] = None
    
    @model_validator(mode="after")
    def update_details(self) -> "PerformanceMetricsEvent":
        """Update details with specialized fields."""
        self.details.update({
            "operation_type": self.operation_type,
            "metrics": self.metrics.model_dump(),
        })
        
        if self.model:
            self.details["model"] = self.model
            
        if self.provider:
            self.details["provider"] = self.provider
            
        if self.component:
            self.details["component"] = self.component
            
        return self


class SystemErrorEvent(AuditEvent):
    """Audit event for system errors.
    
    Attributes:
        error_type: Type of error
        error_message: Error message
        stack_trace: Stack trace of the error
        component: Component where the error occurred
    """
    
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    component: str
    
    def __init__(self, **data: Any) -> None:
        """Initialize with severity HIGH."""
        if "severity" not in data:
            data["severity"] = SeverityLevel.HIGH
        super().__init__(**data)
        
    @model_validator(mode="after")
    def update_details(self) -> "SystemErrorEvent":
        """Update details with specialized fields."""
        self.details.update({
            "error_type": self.error_type,
            "error_message": self.error_message,
            "component": self.component,
        })
        
        if self.stack_trace:
            self.details["stack_trace"] = self.stack_trace
            
        return self


class ConfigurationChangeEvent(AuditEvent):
    """Audit event for configuration changes.
    
    Attributes:
        config_section: Section of configuration being changed
        old_value: Previous configuration value
        new_value: New configuration value
        changed_by: Identifier of who made the change
    """
    
    config_section: str
    old_value: Any
    new_value: Any
    changed_by: Optional[str] = None
    
    @model_validator(mode="after")
    def update_details(self) -> "ConfigurationChangeEvent":
        """Update details with specialized fields."""
        self.details.update({
            "config_section": self.config_section,
            "old_value": self.old_value,
            "new_value": self.new_value,
        })
        
        if self.changed_by:
            self.details["changed_by"] = self.changed_by
            
        return self


# Helper functions to create specific event types

def create_chat_request_event(
    model: str,
    provider: str,
    request_data: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metrics: Optional[OperationMetrics] = None,
) -> ChatOperationEvent:
    """Create a chat request audit event.
    
    Args:
        model: Model identifier
        provider: Provider name
        request_data: Request data summary
        user_id: Optional user identifier
        session_id: Optional session identifier
        metrics: Optional performance metrics
        
    Returns:
        Chat request audit event
    """
    return ChatOperationEvent(
        event_type=AuditEventType.CHAT_REQUEST,
        model=model,
        provider=provider,
        request_data=request_data,
        user_id=user_id,
        session_id=session_id,
        metrics=metrics,
    )


def create_chat_response_event(
    model: str,
    provider: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metrics: Optional[OperationMetrics] = None,
    request_id: Optional[str] = None,
) -> ChatOperationEvent:
    """Create a chat response audit event.
    
    Args:
        model: Model identifier
        provider: Provider name
        request_data: Request data summary
        response_data: Response data summary
        user_id: Optional user identifier
        session_id: Optional session identifier
        metrics: Optional performance metrics
        request_id: Optional request identifier to link with request event
        
    Returns:
        Chat response audit event
    """
    event = ChatOperationEvent(
        event_type=AuditEventType.CHAT_RESPONSE,
        model=model,
        provider=provider,
        request_data=request_data,
        response_data=response_data,
        user_id=user_id,
        session_id=session_id,
        metrics=metrics,
    )
    
    if request_id:
        event.request_id = request_id
        
    return event


def create_compliance_violation_event(
    policy_name: str,
    violation_type: str,
    severity: SeverityLevel,
    action_taken: str,
    violation_details: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    resource_id: Optional[str] = None,
) -> ComplianceViolationEvent:
    """Create a compliance violation audit event.
    
    Args:
        policy_name: Name of the violated policy
        violation_type: Type of violation
        severity: Severity level of the violation
        action_taken: Action taken in response
        violation_details: Details of the violation
        user_id: Optional user identifier
        session_id: Optional session identifier
        resource_id: Optional resource identifier
        
    Returns:
        Compliance violation audit event
    """
    return ComplianceViolationEvent(
        event_type=AuditEventType.COMPLIANCE_VIOLATION,
        policy_name=policy_name,
        violation_type=violation_type,
        severity=severity,
        action_taken=action_taken,
        violation_details=violation_details,
        user_id=user_id,
        session_id=session_id,
        resource_id=resource_id,
    )


def create_performance_metrics_event(
    operation_type: str,
    metrics: OperationMetrics,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    component: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> PerformanceMetricsEvent:
    """Create a performance metrics audit event.
    
    Args:
        operation_type: Type of operation being measured
        metrics: Performance metrics data
        model: Optional model identifier
        provider: Optional provider name
        component: Optional component name
        user_id: Optional user identifier
        session_id: Optional session identifier
        
    Returns:
        Performance metrics audit event
    """
    return PerformanceMetricsEvent(
        event_type=AuditEventType.LATENCY_REPORT,
        operation_type=operation_type,
        metrics=metrics,
        model=model,
        provider=provider,
        component=component,
        user_id=user_id,
        session_id=session_id,
    )


def create_system_error_event(
    error_type: str,
    error_message: str,
    component: str,
    stack_trace: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> SystemErrorEvent:
    """Create a system error audit event.
    
    Args:
        error_type: Type of error
        error_message: Error message
        component: Component where the error occurred
        stack_trace: Optional stack trace
        user_id: Optional user identifier
        session_id: Optional session identifier
        
    Returns:
        System error audit event
    """
    return SystemErrorEvent(
        event_type=AuditEventType.SYSTEM_ERROR,
        error_type=error_type,
        error_message=error_message,
        component=component,
        stack_trace=stack_trace,
        user_id=user_id,
        session_id=session_id,
    )