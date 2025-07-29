"""DeepSentinel SDK exception hierarchy.

This module defines all custom exceptions used throughout the DeepSentinel SDK,
providing clear error types for different failure scenarios.
"""

from typing import Any, Dict, Optional


class DeepSentinelError(Exception):
    """Base exception for all DeepSentinel SDK errors.
    
    All SDK-specific exceptions inherit from this base class to provide
    a consistent exception hierarchy and error handling interface.
    
    Attributes:
        message: Human-readable error message
        error_code: Optional error code for programmatic handling
        details: Optional dictionary containing additional error context
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def __repr__(self) -> str:
        """Return detailed representation of the exception."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"details={self.details!r})"
        )


class ComplianceViolationError(DeepSentinelError):
    """Raised when content violates compliance policies.
    
    This exception is raised when the compliance middleware detects
    content that violates configured compliance policies, such as
    PII detection, content filtering, or security violations.
    
    Attributes:
        policy_name: Name of the violated policy
        violation_type: Type of violation detected
        severity: Severity level of the violation
    """
    
    def __init__(
        self,
        message: str,
        policy_name: str,
        violation_type: str,
        severity: str = "high",
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the compliance violation exception.
        
        Args:
            message: Human-readable error message
            policy_name: Name of the violated policy
            violation_type: Type of violation detected
            severity: Severity level of the violation
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, error_code, details)
        self.policy_name = policy_name
        self.violation_type = violation_type
        self.severity = severity


class ProviderError(DeepSentinelError):
    """Raised when there are issues with LLM provider operations.
    
    This exception covers various provider-related errors including
    authentication failures, rate limiting, API errors, and
    provider-specific issues.
    
    Attributes:
        provider_name: Name of the LLM provider
        status_code: HTTP status code if applicable
        provider_error: Original error from the provider
    """
    
    def __init__(
        self,
        message: str,
        provider_name: str,
        status_code: Optional[int] = None,
        provider_error: Optional[Exception] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the provider error exception.
        
        Args:
            message: Human-readable error message
            provider_name: Name of the LLM provider
            status_code: HTTP status code if applicable
            provider_error: Original error from the provider
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, error_code, details)
        self.provider_name = provider_name
        self.status_code = status_code
        self.provider_error = provider_error


class ConfigurationError(DeepSentinelError):
    """Raised when there are configuration-related issues.
    
    This exception is raised for various configuration problems including
    invalid configuration values, missing required settings, conflicting
    options, and environment setup issues.
    
    Attributes:
        config_key: The configuration key that caused the error
        config_value: The problematic configuration value
    """
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the configuration error exception.
        
        Args:
            message: Human-readable error message
            config_key: The configuration key that caused the error
            config_value: The problematic configuration value
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, error_code, details)
        self.config_key = config_key
        self.config_value = config_value


class MCPError(DeepSentinelError):
    """Raised when there are Model Context Protocol (MCP) related issues.
    
    This exception covers MCP server communication errors, tool execution
    failures, resource access issues, and protocol-level problems.
    
    Attributes:
        server_name: Name of the MCP server
        tool_name: Name of the MCP tool if applicable
        operation: The MCP operation that failed
    """
    
    def __init__(
        self,
        message: str,
        server_name: Optional[str] = None,
        tool_name: Optional[str] = None,
        operation: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the MCP error exception.
        
        Args:
            message: Human-readable error message
            server_name: Name of the MCP server
            tool_name: Name of the MCP tool if applicable
            operation: The MCP operation that failed
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, error_code, details)
        self.server_name = server_name
        self.tool_name = tool_name
        self.operation = operation


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""
    
    def __init__(
        self,
        message: str,
        provider_name: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the authentication error exception.
        
        Args:
            message: Human-readable error message
            provider_name: Name of the LLM provider
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(
            message=message,
            provider_name=provider_name,
            status_code=401,
            error_code=error_code,
            details=details,
        )


class RateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""
    
    def __init__(
        self,
        message: str,
        provider_name: str,
        retry_after: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the rate limit error exception.
        
        Args:
            message: Human-readable error message
            provider_name: Name of the LLM provider
            retry_after: Seconds to wait before retrying
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(
            message=message,
            provider_name=provider_name,
            status_code=429,
            error_code=error_code,
            details=details,
        )
        self.retry_after = retry_after


class ValidationError(DeepSentinelError):
    """Raised when data validation fails."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the validation error exception.
        
        Args:
            message: Human-readable error message
            field_name: Name of the field that failed validation
            field_value: The invalid field value
            error_code: Optional error code for programmatic handling
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, error_code, details)
        self.field_name = field_name
        self.field_value = field_value