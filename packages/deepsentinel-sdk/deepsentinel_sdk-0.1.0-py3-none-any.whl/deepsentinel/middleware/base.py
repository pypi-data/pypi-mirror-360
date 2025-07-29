"""Base middleware for compliance and processing pipeline.

This module provides the foundation for compliance middleware that processes
requests and responses through a configurable pipeline of checks and
transformations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..config import CompliancePolicy, SentinelConfig
from ..exceptions import ComplianceViolationError
from ..types import (
    AuditEntry,
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    ComplianceCheck,
    EmbeddingRequest,
    EmbeddingResponse,
)


class ComplianceMiddleware:
    """Compliance middleware for processing requests and responses.
    
    This class implements a pipeline of compliance checks and transformations
    that can be applied to LLM requests and responses to ensure they meet
    organizational policies and regulatory requirements.
    
    Attributes:
        config: Sentinel configuration
        policies: List of compliance policies
        audit_enabled: Whether audit logging is enabled
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the compliance middleware.
        
        Args:
            config: Sentinel configuration containing policies and settings
        """
        self.config = config
        self.policies = config.compliance_policies
        self.audit_enabled = config.audit_config.enabled
        self._audit_entries: List[AuditEntry] = []
        self._processors: Dict[str, Any] = {}
        
        # Initialize processors based on policies
        self._initialize_processors()
    
    def _initialize_processors(self) -> None:
        """Initialize compliance processors based on configured policies."""
        # This will be expanded as we implement specific processors
        self._processors = {
            "pii_detection": self._create_pii_processor(),
            "content_filter": self._create_content_filter_processor(),
            "audit_logger": self._create_audit_processor(),
        }
    
    def _create_pii_processor(self) -> Any:
        """Create PII detection processor."""
        # Placeholder for PII detection processor
        return None
    
    def _create_content_filter_processor(self) -> Any:
        """Create content filtering processor."""
        # Placeholder for content filtering processor
        return None
    
    def _create_audit_processor(self) -> Any:
        """Create audit logging processor."""
        # Placeholder for audit logging processor
        return None
    
    async def process_request(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatRequest, CompletionRequest, EmbeddingRequest]:
        """Process a request through the compliance pipeline.
        
        Args:
            request: The request to process
            context: Optional context information
            
        Returns:
            Processed request (may be modified)
            
        Raises:
            ComplianceViolationError: If request violates policies
        """
        context = context or {}
        
        # Start audit entry
        audit_entry = None
        if self.audit_enabled:
            audit_entry = self._create_audit_entry(request, context)
        
        # Run compliance checks
        compliance_checks = await self._run_compliance_checks(
            request, "request", context
        )
        
        # Check for violations
        violations = [check for check in compliance_checks if not check.passed]
        if violations:
            blocking_violations = [
                v for v in violations
                if v.action.value in ["block", "error"]
            ]
            if blocking_violations:
                violation = blocking_violations[0]
                if audit_entry:
                    audit_entry.compliance_checks = compliance_checks
                    self._audit_entries.append(audit_entry)
                
                raise ComplianceViolationError(
                    message=violation.message,
                    policy_name=violation.policy_name,
                    violation_type=violation.policy_name,
                    severity=violation.severity.value,
                )
        
        # Apply transformations
        processed_request = await self._apply_transformations(
            request, compliance_checks, "request"
        )
        
        # Update audit entry
        if audit_entry:
            audit_entry.compliance_checks = compliance_checks
            audit_entry.request_data = self._sanitize_request_data(
                processed_request
            )
        
        return processed_request
    
    async def process_response(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatResponse, CompletionResponse, EmbeddingResponse]:
        """Process a response through the compliance pipeline.
        
        Args:
            response: The response to process
            request: The original request
            context: Optional context information
            
        Returns:
            Processed response (may be modified)
            
        Raises:
            ComplianceViolationError: If response violates policies
        """
        context = context or {}
        
        # Run compliance checks on response
        compliance_checks = await self._run_compliance_checks(
            response, "response", context
        )
        
        # Check for violations
        violations = [check for check in compliance_checks if not check.passed]
        if violations:
            blocking_violations = [
                v for v in violations
                if v.action.value in ["block", "error"]
            ]
            if blocking_violations:
                violation = blocking_violations[0]
                raise ComplianceViolationError(
                    message=violation.message,
                    policy_name=violation.policy_name,
                    violation_type=violation.policy_name,
                    severity=violation.severity.value,
                )
        
        # Apply transformations
        processed_response = await self._apply_transformations(
            response, compliance_checks, "response"
        )
        
        # Update audit entry if we have one
        if self.audit_enabled and self._audit_entries:
            audit_entry = self._audit_entries[-1]
            audit_entry.response_data = self._sanitize_response_data(
                processed_response
            )
            audit_entry.compliance_checks.extend(compliance_checks)
        
        return processed_response
    
    async def _run_compliance_checks(
        self,
        data: Any,
        data_type: str,
        context: Dict[str, Any],
    ) -> List[ComplianceCheck]:
        """Run compliance checks on the given data.
        
        Args:
            data: Data to check
            data_type: Type of data ("request" or "response")
            context: Context information
            
        Returns:
            List of compliance check results
        """
        checks = []
        
        for policy in self.policies:
            if not policy.enabled:
                continue
            
            check = await self._run_policy_check(
                policy, data, data_type, context
            )
            if check:
                checks.append(check)
        
        return checks
    
    async def _run_policy_check(
        self,
        policy: CompliancePolicy,
        data: Any,
        data_type: str,
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Run a specific policy check.
        
        Args:
            policy: Policy to check
            data: Data to check
            data_type: Type of data
            context: Context information
            
        Returns:
            Compliance check result or None if not applicable
        """
        # This is a placeholder implementation
        # Real implementations would depend on the specific policy type
        
        check = ComplianceCheck(
            policy_name=policy.name,
            passed=True,  # Default to passing
            action=policy.action,
            severity=policy.severity,
            message=f"Policy '{policy.name}' check passed",
        )
        
        # Add policy-specific logic here
        if policy.name == "pii_detection":
            # PII detection logic would go here
            pass
        elif policy.name == "content_filter":
            # Content filtering logic would go here
            pass
        
        return check
    
    async def _apply_transformations(
        self,
        data: Any,
        compliance_checks: List[ComplianceCheck],
        data_type: str,
    ) -> Any:
        """Apply transformations based on compliance check results.
        
        Args:
            data: Data to transform
            compliance_checks: Results of compliance checks
            data_type: Type of data
            
        Returns:
            Transformed data
        """
        # This is a placeholder implementation
        # Real implementations would apply specific transformations
        # based on the compliance check results
        
        transformed_data = data
        
        for check in compliance_checks:
            if check.action.value == "redact":
                # Apply redaction transformations
                transformed_data = await self._apply_redaction(
                    transformed_data, check
                )
            elif check.action.value == "warn":
                # Add warning metadata
                if hasattr(transformed_data, 'metadata'):
                    if not hasattr(transformed_data.metadata, 'warnings'):
                        transformed_data.metadata['warnings'] = []
                    transformed_data.metadata['warnings'].append(check.message)
        
        return transformed_data
    
    async def _apply_redaction(self, data: Any, check: ComplianceCheck) -> Any:
        """Apply redaction transformations to data.
        
        Args:
            data: Data to redact
            check: Compliance check that triggered redaction
            
        Returns:
            Redacted data
        """
        # Placeholder for redaction logic
        return data
    
    def _create_audit_entry(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Dict[str, Any],
    ) -> AuditEntry:
        """Create an audit entry for the request.
        
        Args:
            request: The request being processed
            context: Context information
            
        Returns:
            New audit entry
        """
        return AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=context.get("user_id"),
            session_id=context.get("session_id"),
            operation=context.get("operation", "unknown"),
            provider=context.get("provider", "unknown"),
            model=getattr(request, "model", "unknown"),
            request_data=self._sanitize_request_data(request),
            metadata=context.copy(),
        )
    
    def _sanitize_request_data(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
    ) -> Dict[str, Any]:
        """Sanitize request data for audit logging.
        
        Args:
            request: Request to sanitize
            
        Returns:
            Sanitized request data
        """
        # Convert to dict and remove sensitive information
        data = request.dict() if hasattr(request, 'dict') else {}
        
        # Remove or mask sensitive fields based on configuration
        if not self.config.audit_config.include_request_body:
            data.pop("messages", None)
            data.pop("prompt", None)
            data.pop("input", None)
        
        return data
    
    def _sanitize_response_data(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
    ) -> Dict[str, Any]:
        """Sanitize response data for audit logging.
        
        Args:
            response: Response to sanitize
            
        Returns:
            Sanitized response data
        """
        # Convert to dict and remove sensitive information
        data = response.dict() if hasattr(response, 'dict') else {}
        
        # Remove or mask sensitive fields based on configuration
        if not self.config.audit_config.include_response_body:
            data.pop("choices", None)
            data.pop("data", None)
        
        return data
    
    def get_audit_entries(self) -> List[AuditEntry]:
        """Get all audit entries.
        
        Returns:
            List of audit entries
        """
        return self._audit_entries.copy()
    
    def clear_audit_entries(self) -> None:
        """Clear all stored audit entries."""
        self._audit_entries.clear()
    
    def add_policy(self, policy: CompliancePolicy) -> None:
        """Add a compliance policy.
        
        Args:
            policy: Policy to add
        """
        # Remove existing policy with the same name
        self.policies = [p for p in self.policies if p.name != policy.name]
        self.policies.append(policy)
    
    def remove_policy(self, policy_name: str) -> None:
        """Remove a compliance policy.
        
        Args:
            policy_name: Name of the policy to remove
        """
        self.policies = [p for p in self.policies if p.name != policy_name]
    
    def get_policy(self, policy_name: str) -> Optional[CompliancePolicy]:
        """Get a compliance policy by name.
        
        Args:
            policy_name: Name of the policy
            
        Returns:
            Policy if found, None otherwise
        """
        for policy in self.policies:
            if policy.name == policy_name:
                return policy
        return None
    
    async def __aenter__(self) -> "ComplianceMiddleware":
        """Async context manager entry."""
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        # Clean up resources if needed
        pass
    
    def __repr__(self) -> str:
        """Return string representation of the middleware."""
        return (
            f"ComplianceMiddleware("
            f"policies={len(self.policies)}, "
            f"audit_enabled={self.audit_enabled})"
        )