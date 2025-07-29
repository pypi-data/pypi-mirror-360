"""Base middleware for compliance and processing pipeline.

This module provides the foundation for compliance middleware that processes
requests and responses through a configurable pipeline of checks and
transformations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..api.audit import AuditAPI
from ..api.client import DeepSentinelAPIClient
from ..api.compliance import ComplianceAPI
from ..compliance.engine import ComplianceEngine
from ..compliance.interceptor import ComplianceInterceptor
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
        
        # Initialize compliance components
        self._compliance_engine = ComplianceEngine(config)
        self._compliance_interceptor = ComplianceInterceptor(
            self._compliance_engine
        )
        
        # Initialize API clients if API integration is enabled
        self._api_client = None
        self._compliance_api = None
        self._audit_api = None
        
        if config.api_integration_enabled and config.api_key:
            self._api_client = DeepSentinelAPIClient(config)
            self._compliance_api = ComplianceAPI(self._api_client)
            self._audit_api = AuditAPI(self._api_client)
        
        # Initialize processors based on policies
        self._processors: Dict[str, Any] = {}
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
        return self._compliance_engine.detection_engine.get_engine(
            "pii_detector"
        )
    
    def _create_content_filter_processor(self) -> Any:
        """Create content filtering processor."""
        # Return pattern matcher for content filtering
        return self._compliance_engine.detection_engine.get_engine(
            "pattern_matcher"
        )
    
    def _create_audit_processor(self) -> Any:
        """Create audit logging processor."""
        # Return audit API client if available, otherwise None
        return self._audit_api
    
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
        # Use the compliance engine for checks
        if data_type == "request":
            # Use local detection via compliance engine
            text_content = self._extract_text_content(data)
            engine = self._compliance_engine.detection_engine
            detection_results = await engine.analyze_text(
                text_content,
                context
            )
            
            # Evaluate against policies
            policy_mgr = self._compliance_engine.policy_manager
            return await policy_mgr.evaluate_request(
                data,
                detection_results,
                context
            )
        else:
            # For responses, need both request and response
            request = context.get("original_request")
            text_content = self._extract_text_content(data)
            engine = self._compliance_engine.detection_engine
            detection_results = await engine.analyze_text(
                text_content,
                context
            )
            
            # Evaluate against policies
            policy_mgr = self._compliance_engine.policy_manager
            return await policy_mgr.evaluate_response(
                data,
                request,
                detection_results,
                context
            )
    
    def _extract_text_content(self, data: Any) -> List[str]:
        """Extract text content from request/response for analysis.
        
        Args:
            data: Data to extract text from
            
        Returns:
            List of text strings to analyze
        """
        # Delegate to the compliance engine's extraction methods
        if isinstance(
            data, (ChatRequest, CompletionRequest, EmbeddingRequest)
        ):
            return self._compliance_engine._extract_request_text(data)
        else:
            return self._compliance_engine._extract_response_text(data)
    
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
        # Use the compliance engine for transformations
        detection_results = {}
        
        # Extract detection results from compliance checks
        for check in compliance_checks:
            if "detection_results" in check.details:
                detection_results.update(check.details["detection_results"])
        
        if data_type == "request":
            # Transform request data
            engine = self._compliance_engine
            return await engine._apply_request_transformations(
                data,
                compliance_checks,
                detection_results
            )
        else:
            # Transform response data
            engine = self._compliance_engine
            return await engine._apply_response_transformations(
                data,
                compliance_checks,
                detection_results
            )
    
    async def initialize(self) -> None:
        """Initialize middleware components."""
        # Initialize API client if available
        if self._api_client:
            await self._api_client.initialize()
        
        # Initialize compliance engine
        await self._compliance_engine.reload_policies(self.policies)
    
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
    
    async def cleanup(self) -> None:
        """Clean up middleware resources."""
        # Close API client if available
        if self._api_client:
            await self._api_client.close()
        
    def get_audit_entries(self) -> List[AuditEntry]:
        """Get all audit entries.
        
        Returns:
            List of audit entries
        """
        return self._audit_entries.copy()
    
    def clear_audit_entries(self) -> None:
        """Clear all stored audit entries."""
        self._audit_entries.clear()
        
    async def submit_audit_entries(self) -> bool:
        """Submit audit entries to the audit API if enabled.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._audit_api or not self.audit_enabled:
            return False
            
        try:
            # Convert entries to API format
            api_entries = [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": entry.user_id,
                    "session_id": entry.session_id,
                    "operation": entry.operation,
                    "provider": entry.provider,
                    "model": entry.model,
                    "request_data": entry.request_data,
                    "response_data": entry.response_data,
                    "metadata": entry.metadata,
                }
                for entry in self._audit_entries
            ]
            
            # Submit in batch
            if api_entries:
                await self._audit_api.log_batch_events(api_entries)
                self.clear_audit_entries()
                return True
                
        except Exception:
            # Log error but don't raise
            return False
            
        return True
    
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
        await self.initialize()
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        # Submit any remaining audit entries
        if self.audit_enabled:
            await self.submit_audit_entries()
            
        # Clean up resources
        await self.cleanup()
    
    def __repr__(self) -> str:
        """Return string representation of the middleware."""
        return (
            f"ComplianceMiddleware("
            f"policies={len(self.policies)}, "
            f"audit_enabled={self.audit_enabled})"
        )