"""Request/response interceptor for compliance checking.

This module provides interceptor functionality that can be integrated
into HTTP clients and middleware to automatically apply compliance
checks to all requests and responses.
"""

import time
from typing import Any, Callable, Dict, Optional, Union

import structlog

from ..exceptions import ComplianceViolationError
from ..types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
)
from .engine import ComplianceEngine


class ComplianceInterceptor:
    """Interceptor for automatic compliance checking.
    
    This class provides interceptor functionality that can be integrated
    into HTTP clients, middleware, or other components to automatically
    apply compliance checks to requests and responses.
    
    Attributes:
        engine: Compliance engine instance
        logger: Structured logger
        enabled: Whether the interceptor is enabled
        bypass_rules: Rules for bypassing compliance checks
    """
    
    def __init__(
        self,
        engine: ComplianceEngine,
        enabled: bool = True,
        bypass_rules: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the compliance interceptor.
        
        Args:
            engine: Compliance engine to use for checks
            enabled: Whether the interceptor is enabled
            bypass_rules: Optional rules for bypassing compliance checks
        """
        self.engine = engine
        self.enabled = enabled
        self.bypass_rules = bypass_rules or {}
        self.logger = structlog.get_logger(__name__)
        
        # Performance metrics
        self._intercepted_requests = 0
        self._intercepted_responses = 0
        self._bypassed_requests = 0
        self._violations_blocked = 0
        
        self.logger.info(
            "Compliance interceptor initialized",
            enabled=self.enabled,
            bypass_rules=len(self.bypass_rules),
        )
    
    async def intercept_request(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatRequest, CompletionRequest, EmbeddingRequest]:
        """Intercept and process a request through compliance checks.
        
        Args:
            request: Request to intercept and check
            context: Optional context information
            
        Returns:
            Processed request (may be modified)
            
        Raises:
            ComplianceViolationError: If request violates compliance policies
        """
        if not self.enabled:
            return request
        
        context = context or {}
        self._intercepted_requests += 1
        
        # Check bypass rules
        if self._should_bypass_request(request, context):
            self._bypassed_requests += 1
            self.logger.debug(
                "Request bypassed compliance check",
                reason="bypass_rule_matched",
            )
            return request
        
        start_time = time.time()
        
        try:
            # Process through compliance engine
            processed_request = await self.engine.process_request(
                request, context
            )
            
            duration = (time.time() - start_time) * 1000
            
            self.logger.debug(
                "Request compliance check completed",
                duration_ms=duration,
                request_type=type(request).__name__,
            )
            
            return processed_request
            
        except ComplianceViolationError as e:
            self._violations_blocked += 1
            self.logger.warning(
                "Request blocked by compliance check",
                policy=e.policy_name,
                violation_type=e.violation_type,
                severity=e.severity,
            )
            raise
        except Exception as e:
            self.logger.error(
                "Request compliance check failed",
                error=str(e),
                request_type=type(request).__name__,
            )
            # Decide whether to block or allow on error
            if self._should_block_on_error(context):
                raise ComplianceViolationError(
                    message=f"Compliance check failed: {str(e)}",
                    policy_name="system_error",
                    violation_type="system_error",
                    severity="high",
                ) from e
            else:
                # Log error but allow request to proceed
                return request
    
    async def intercept_response(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatResponse, CompletionResponse, EmbeddingResponse]:
        """Intercept and process a response through compliance checks.
        
        Args:
            response: Response to intercept and check
            request: Original request
            context: Optional context information
            
        Returns:
            Processed response (may be modified)
            
        Raises:
            ComplianceViolationError: If response violates compliance policies
        """
        if not self.enabled:
            return response
        
        context = context or {}
        self._intercepted_responses += 1
        
        # Check bypass rules
        if self._should_bypass_response(response, request, context):
            self.logger.debug(
                "Response bypassed compliance check",
                reason="bypass_rule_matched",
            )
            return response
        
        start_time = time.time()
        
        try:
            # Process through compliance engine
            processed_response = await self.engine.process_response(
                response, request, context
            )
            
            duration = (time.time() - start_time) * 1000
            
            self.logger.debug(
                "Response compliance check completed",
                duration_ms=duration,
                response_type=type(response).__name__,
            )
            
            return processed_response
            
        except ComplianceViolationError as e:
            self._violations_blocked += 1
            self.logger.warning(
                "Response blocked by compliance check",
                policy=e.policy_name,
                violation_type=e.violation_type,
                severity=e.severity,
            )
            raise
        except Exception as e:
            self.logger.error(
                "Response compliance check failed",
                error=str(e),
                response_type=type(response).__name__,
            )
            # Decide whether to block or allow on error
            if self._should_block_on_error(context):
                raise ComplianceViolationError(
                    message=f"Compliance check failed: {str(e)}",
                    policy_name="system_error",
                    violation_type="system_error",
                    severity="high",
                ) from e
            else:
                # Log error but allow response to proceed
                return response
    
    def _should_bypass_request(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Dict[str, Any],
    ) -> bool:
        """Check if request should bypass compliance checks.
        
        Args:
            request: Request to check
            context: Context information
            
        Returns:
            True if request should bypass compliance checks
        """
        # Check context-based bypass rules
        if self.bypass_rules.get("bypass_on_debug") and context.get("debug"):
            return True
        
        # Check user-based bypass rules
        bypass_users = self.bypass_rules.get("bypass_users", [])
        if context.get("user_id") in bypass_users:
            return True
        
        # Check operation-based bypass rules
        bypass_operations = self.bypass_rules.get("bypass_operations", [])
        if context.get("operation") in bypass_operations:
            return True
        
        # Check model-based bypass rules
        bypass_models = self.bypass_rules.get("bypass_models", [])
        if hasattr(request, "model") and request.model in bypass_models:
            return True
        
        return False
    
    def _should_bypass_response(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Dict[str, Any],
    ) -> bool:
        """Check if response should bypass compliance checks.
        
        Args:
            response: Response to check
            request: Original request
            context: Context information
            
        Returns:
            True if response should bypass compliance checks
        """
        # Use same logic as request bypass for consistency
        return self._should_bypass_request(request, context)
    
    def _should_block_on_error(self, context: Dict[str, Any]) -> bool:
        """Determine whether to block requests/responses on compliance errors.
        
        Args:
            context: Context information
            
        Returns:
            True if should block on error, False to allow through
        """
        # Check configuration for error handling behavior
        error_handling = self.bypass_rules.get("error_handling", "block")
        
        if error_handling == "allow":
            return False
        elif error_handling == "block":
            return True
        elif error_handling == "context_dependent":
            # Block in production, allow in development
            environment = context.get("environment", "production")
            return environment == "production"
        
        # Default to blocking
        return True
    
    def create_middleware(
        self,
    ) -> Callable[
        [
            Callable[
                [
                    Union[ChatRequest, CompletionRequest, EmbeddingRequest],
                    Dict[str, Any],
                ],
                Union[ChatResponse, CompletionResponse, EmbeddingResponse],
            ]
        ],
        Callable[
            [
                Union[ChatRequest, CompletionRequest, EmbeddingRequest],
                Dict[str, Any],
            ],
            Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        ],
    ]:
        """Create middleware function that wraps API calls with compliance.
        
        Returns:
            Middleware function that can wrap API calls
        """
        
        async def compliance_middleware(
            next_handler: Callable[
                [
                    Union[ChatRequest, CompletionRequest, EmbeddingRequest],
                    Dict[str, Any],
                ],
                Union[ChatResponse, CompletionResponse, EmbeddingResponse],
            ]
        ) -> Callable[
            [
                Union[ChatRequest, CompletionRequest, EmbeddingRequest],
                Dict[str, Any],
            ],
            Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        ]:
            """Middleware wrapper for compliance checking.
            
            Args:
                next_handler: Next handler in the chain
                
            Returns:
                Wrapped handler with compliance checking
            """
            
            async def wrapped_handler(
                request: Union[
                    ChatRequest, CompletionRequest, EmbeddingRequest
                ],
                context: Dict[str, Any],
            ) -> Union[ChatResponse, CompletionResponse, EmbeddingResponse]:
                """Wrapped handler with compliance checks.
                
                Args:
                    request: Request to process
                    context: Context information
                    
                Returns:
                    Processed response
                """
                # Intercept and check request
                checked_request = await self.intercept_request(
                    request, context
                )
                
                # Call next handler
                response = await next_handler(checked_request, context)
                
                # Intercept and check response
                checked_response = await self.intercept_response(
                    response, checked_request, context
                )
                
                return checked_response
            
            return wrapped_handler
        
        return compliance_middleware
    
    def enable(self) -> None:
        """Enable the interceptor."""
        self.enabled = True
        self.logger.info("Compliance interceptor enabled")
    
    def disable(self) -> None:
        """Disable the interceptor."""
        self.enabled = False
        self.logger.info("Compliance interceptor disabled")
    
    def update_bypass_rules(self, bypass_rules: Dict[str, Any]) -> None:
        """Update bypass rules.
        
        Args:
            bypass_rules: New bypass rules configuration
        """
        self.bypass_rules = bypass_rules
        self.logger.info(
            "Bypass rules updated",
            rule_count=len(bypass_rules),
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get interceptor performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        total_requests = self._intercepted_requests + self._bypassed_requests
        
        return {
            "intercepted_requests": self._intercepted_requests,
            "intercepted_responses": self._intercepted_responses,
            "bypassed_requests": self._bypassed_requests,
            "violations_blocked": self._violations_blocked,
            "total_requests": total_requests,
            "bypass_rate": (
                self._bypassed_requests / max(total_requests, 1)
            ),
            "violation_rate": (
                self._violations_blocked / max(self._intercepted_requests, 1)
            ),
            "enabled": self.enabled,
        }
    
    def reset_metrics(self) -> None:
        """Reset performance metrics counters."""
        self._intercepted_requests = 0
        self._intercepted_responses = 0
        self._bypassed_requests = 0
        self._violations_blocked = 0
        self.logger.info("Interceptor metrics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on interceptor.
        
        Returns:
            Health check results
        """
        try:
            # Check engine health
            engine_health = await self.engine.health_check()
            
            return {
                "status": (
                    "healthy" if engine_health.get("status") == "healthy"
                    else "degraded"
                ),
                "enabled": self.enabled,
                "engine_status": engine_health.get("status"),
                "metrics": self.get_metrics(),
                "bypass_rules": len(self.bypass_rules),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "enabled": self.enabled,
            }