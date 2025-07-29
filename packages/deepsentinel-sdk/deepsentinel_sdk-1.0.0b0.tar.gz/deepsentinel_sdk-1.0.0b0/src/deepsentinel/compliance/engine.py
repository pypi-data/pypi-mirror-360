"""Main compliance processing engine for DeepSentinel SDK.

This module contains the core compliance processing engine that orchestrates
policy evaluation, detection, and enforcement across all compliance checks.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import structlog

from ..config import SentinelConfig
from ..exceptions import ComplianceViolationError, ConfigurationError
from ..types import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    ComplianceAction,
    ComplianceCheck,
    EmbeddingRequest,
    EmbeddingResponse,
    SeverityLevel,
)
from .detection.engine import DetectionEngine
from .policies import PolicyManager


class ComplianceEngine:
    """Main compliance processing engine.
    
    This class orchestrates all compliance checking operations including
    policy evaluation, detection engines, and enforcement actions.
    
    Attributes:
        config: Sentinel configuration
        policy_manager: Policy manager instance
        detection_engine: Detection engine instance
        logger: Structured logger
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the compliance engine.
        
        Args:
            config: Sentinel configuration containing policies and settings
        """
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Initialize components
        self.policy_manager = PolicyManager(config.compliance_policies)
        self.detection_engine = DetectionEngine(config)
        
        # Performance metrics
        self._total_checks = 0
        self._violations_found = 0
        self._start_time = datetime.utcnow()
        
        self.logger.info(
            "Compliance engine initialized",
            policies=len(config.compliance_policies),
            detection_engines=len(self.detection_engine.engines),
        )
    
    async def process_request(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatRequest, CompletionRequest, EmbeddingRequest]:
        """Process a request through compliance checks.
        
        Args:
            request: The request to process
            context: Optional context information
            
        Returns:
            Processed request (may be modified)
            
        Raises:
            ComplianceViolationError: If request violates policies
        """
        context = context or {}
        self._total_checks += 1
        
        start_time = datetime.utcnow()
        
        try:
            # Extract text content from request
            text_content = self._extract_request_text(request)
            
            # Run detection engines
            detection_results = await self.detection_engine.analyze_text(
                text_content, context
            )
            
            # Evaluate policies
            compliance_checks = await self.policy_manager.evaluate_request(
                request, detection_results, context
            )
            
            # Check for violations
            violations = [
                check for check in compliance_checks if not check.passed
            ]
            if violations:
                self._violations_found += len(violations)
                await self._handle_violations(violations, "request")
            
            # Apply transformations
            processed_request = await self._apply_request_transformations(
                request, compliance_checks, detection_results
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Request compliance check completed",
                duration_ms=duration,
                violations=len(violations),
                transformations_applied=len([
                    c for c in compliance_checks 
                    if c.action in [ComplianceAction.REDACT]
                ]),
            )
            
            return processed_request
            
        except Exception as e:
            self.logger.error(
                "Request compliance check failed",
                error=str(e),
                request_type=type(request).__name__,
            )
            raise
    
    async def process_response(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        context: Optional[Dict[str, Any]] = None,
    ) -> Union[ChatResponse, CompletionResponse, EmbeddingResponse]:
        """Process a response through compliance checks.
        
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
        self._total_checks += 1
        
        start_time = datetime.utcnow()
        
        try:
            # Extract text content from response
            text_content = self._extract_response_text(response)
            
            # Run detection engines
            detection_results = await self.detection_engine.analyze_text(
                text_content, context
            )
            
            # Evaluate policies
            compliance_checks = await self.policy_manager.evaluate_response(
                response, request, detection_results, context
            )
            
            # Check for violations
            violations = [
                check for check in compliance_checks if not check.passed
            ]
            if violations:
                self._violations_found += len(violations)
                await self._handle_violations(violations, "response")
            
            # Apply transformations
            processed_response = await self._apply_response_transformations(
                response, compliance_checks, detection_results
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            self.logger.info(
                "Response compliance check completed",
                duration_ms=duration,
                violations=len(violations),
                transformations_applied=len([
                    c for c in compliance_checks 
                    if c.action in [ComplianceAction.REDACT]
                ]),
            )
            
            return processed_response
            
        except Exception as e:
            self.logger.error(
                "Response compliance check failed",
                error=str(e),
                response_type=type(response).__name__,
            )
            raise
    
    async def _handle_violations(
        self, violations: List[ComplianceCheck], data_type: str
    ) -> None:
        """Handle compliance violations based on policy actions.
        
        Args:
            violations: List of compliance violations
            data_type: Type of data being checked ("request" or "response")
            
        Raises:
            ComplianceViolationError: If blocking violations are found
        """
        # Sort violations by severity
        blocking_violations = [
            v for v in violations
            if v.action in [ComplianceAction.BLOCK]
        ]
        
        if blocking_violations:
            # Find the most severe violation
            severity_order = {
                SeverityLevel.CRITICAL: 4,
                SeverityLevel.HIGH: 3,
                SeverityLevel.MEDIUM: 2,
                SeverityLevel.LOW: 1,
            }
            
            most_severe = max(
                blocking_violations,
                key=lambda v: severity_order.get(v.severity, 0)
            )
            
            self.logger.error(
                "Blocking compliance violation detected",
                policy=most_severe.policy_name,
                severity=most_severe.severity.value,
                action=most_severe.action.value,
                data_type=data_type,
            )
            
            raise ComplianceViolationError(
                message=most_severe.message,
                policy_name=most_severe.policy_name,
                violation_type=most_severe.policy_name,
                severity=most_severe.severity.value,
            )
        
        # Log warnings for non-blocking violations
        for violation in violations:
            if violation.action == ComplianceAction.WARN:
                self.logger.warning(
                    "Compliance warning",
                    policy=violation.policy_name,
                    severity=violation.severity.value,
                    message=violation.message,
                    data_type=data_type,
                )
    
    def _extract_request_text(
        self, request: Union[ChatRequest, CompletionRequest, EmbeddingRequest]
    ) -> List[str]:
        """Extract text content from request for analysis.
        
        Args:
            request: Request to extract text from
            
        Returns:
            List of text strings to analyze
        """
        text_content = []
        
        if isinstance(request, ChatRequest):
            for message in request.messages:
                if message.content:
                    text_content.append(message.content)
        elif isinstance(request, CompletionRequest):
            if isinstance(request.prompt, str):
                text_content.append(request.prompt)
            elif isinstance(request.prompt, list):
                text_content.extend(request.prompt)
        elif isinstance(request, EmbeddingRequest):
            if isinstance(request.input, str):
                text_content.append(request.input)
            elif isinstance(request.input, list):
                text_content.extend(request.input)
        
        return text_content
    
    def _extract_response_text(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse]
    ) -> List[str]:
        """Extract text content from response for analysis.
        
        Args:
            response: Response to extract text from
            
        Returns:
            List of text strings to analyze
        """
        text_content = []
        
        if isinstance(response, ChatResponse):
            for choice in response.choices:
                if choice.message.content:
                    text_content.append(choice.message.content)
        elif isinstance(response, CompletionResponse):
            for choice in response.choices:
                text_content.append(choice.text)
        # EmbeddingResponse doesn't contain text to analyze
        
        return text_content
    
    async def _apply_request_transformations(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        compliance_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> Union[ChatRequest, CompletionRequest, EmbeddingRequest]:
        """Apply transformations to request based on compliance results.
        
        Args:
            request: Request to transform
            compliance_checks: Compliance check results
            detection_results: Detection engine results
            
        Returns:
            Transformed request
        """
        # Apply redaction transformations
        redaction_checks = [
            c for c in compliance_checks 
            if c.action == ComplianceAction.REDACT
        ]
        
        if not redaction_checks:
            return request
        
        # Create a copy of the request for modification
        if isinstance(request, ChatRequest):
            return await self._redact_chat_request(
                request, redaction_checks, detection_results
            )
        elif isinstance(request, CompletionRequest):
            return await self._redact_completion_request(
                request, redaction_checks, detection_results
            )
        elif isinstance(request, EmbeddingRequest):
            return await self._redact_embedding_request(
                request, redaction_checks, detection_results
            )
        
        return request
    
    async def _apply_response_transformations(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        compliance_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> Union[ChatResponse, CompletionResponse, EmbeddingResponse]:
        """Apply transformations to response based on compliance results.
        
        Args:
            response: Response to transform
            compliance_checks: Compliance check results
            detection_results: Detection engine results
            
        Returns:
            Transformed response
        """
        # Apply redaction transformations
        redaction_checks = [
            c for c in compliance_checks 
            if c.action == ComplianceAction.REDACT
        ]
        
        if not redaction_checks:
            return response
        
        # Create a copy of the response for modification
        if isinstance(response, ChatResponse):
            return await self._redact_chat_response(
                response, redaction_checks, detection_results
            )
        elif isinstance(response, CompletionResponse):
            return await self._redact_completion_response(
                response, redaction_checks, detection_results
            )
        
        return response
    
    async def _redact_chat_request(
        self,
        request: ChatRequest,
        redaction_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> ChatRequest:
        """Apply redaction to chat request messages.
        
        Args:
            request: Chat request to redact
            redaction_checks: Redaction compliance checks
            detection_results: Detection results with locations
            
        Returns:
            Redacted chat request
        """
        # Create a copy with redacted messages
        redacted_messages = []
        for message in request.messages:
            if message.content:
                redacted_content = await self._apply_text_redaction(
                    message.content, detection_results
                )
                redacted_message = message.copy()
                redacted_message.content = redacted_content
                redacted_messages.append(redacted_message)
            else:
                redacted_messages.append(message)
        
        # Create new request with redacted messages
        redacted_request = request.copy()
        redacted_request.messages = redacted_messages
        return redacted_request
    
    async def _redact_completion_request(
        self,
        request: CompletionRequest,
        redaction_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> CompletionRequest:
        """Apply redaction to completion request prompt.
        
        Args:
            request: Completion request to redact
            redaction_checks: Redaction compliance checks
            detection_results: Detection results with locations
            
        Returns:
            Redacted completion request
        """
        redacted_request = request.copy()
        
        if isinstance(request.prompt, str):
            redacted_request.prompt = await self._apply_text_redaction(
                request.prompt, detection_results
            )
        elif isinstance(request.prompt, list):
            redacted_prompts = []
            for prompt in request.prompt:
                redacted_prompt = await self._apply_text_redaction(
                    prompt, detection_results
                )
                redacted_prompts.append(redacted_prompt)
            redacted_request.prompt = redacted_prompts
        
        return redacted_request
    
    async def _redact_embedding_request(
        self,
        request: EmbeddingRequest,
        redaction_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> EmbeddingRequest:
        """Apply redaction to embedding request input.
        
        Args:
            request: Embedding request to redact
            redaction_checks: Redaction compliance checks
            detection_results: Detection results with locations
            
        Returns:
            Redacted embedding request
        """
        redacted_request = request.copy()
        
        if isinstance(request.input, str):
            redacted_request.input = await self._apply_text_redaction(
                request.input, detection_results
            )
        elif isinstance(request.input, list):
            redacted_inputs = []
            for input_text in request.input:
                redacted_input = await self._apply_text_redaction(
                    input_text, detection_results
                )
                redacted_inputs.append(redacted_input)
            redacted_request.input = redacted_inputs
        
        return redacted_request
    
    async def _redact_chat_response(
        self,
        response: ChatResponse,
        redaction_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> ChatResponse:
        """Apply redaction to chat response messages.
        
        Args:
            response: Chat response to redact
            redaction_checks: Redaction compliance checks
            detection_results: Detection results with locations
            
        Returns:
            Redacted chat response
        """
        redacted_response = response.copy()
        redacted_choices = []
        
        for choice in response.choices:
            if choice.message.content:
                redacted_content = await self._apply_text_redaction(
                    choice.message.content, detection_results
                )
                redacted_choice = choice.copy()
                redacted_choice.message.content = redacted_content
                redacted_choices.append(redacted_choice)
            else:
                redacted_choices.append(choice)
        
        redacted_response.choices = redacted_choices
        return redacted_response
    
    async def _redact_completion_response(
        self,
        response: CompletionResponse,
        redaction_checks: List[ComplianceCheck],
        detection_results: Dict[str, Any],
    ) -> CompletionResponse:
        """Apply redaction to completion response text.
        
        Args:
            response: Completion response to redact
            redaction_checks: Redaction compliance checks
            detection_results: Detection results with locations
            
        Returns:
            Redacted completion response
        """
        redacted_response = response.copy()
        redacted_choices = []
        
        for choice in response.choices:
            redacted_text = await self._apply_text_redaction(
                choice.text, detection_results
            )
            redacted_choice = choice.copy()
            redacted_choice.text = redacted_text
            redacted_choices.append(redacted_choice)
        
        redacted_response.choices = redacted_choices
        return redacted_response
    
    async def _apply_text_redaction(
        self, text: str, detection_results: Dict[str, Any]
    ) -> str:
        """Apply text redaction based on detection results.
        
        Args:
            text: Text to redact
            detection_results: Detection results with sensitive data locations
            
        Returns:
            Redacted text
        """
        # Get redaction patterns from detection results
        redacted_text = text
        
        for engine_name, results in detection_results.items():
            if "matches" in results:
                # Reverse to maintain indices when applying redactions
                for match in reversed(results["matches"]):
                    start = match.get("start", 0)
                    end = match.get("end", len(match.get("text", "")))
                    pattern_type = match.get("type", "SENSITIVE")
                    
                    # Apply appropriate redaction based on pattern type
                    replacement = self._get_redaction_replacement(pattern_type)
                    redacted_text = (
                        redacted_text[:start] + replacement +
                        redacted_text[end:]
                    )
        
        return redacted_text
    
    def _get_redaction_replacement(self, pattern_type: str) -> str:
        """Get appropriate redaction replacement for pattern type.
        
        Args:
            pattern_type: Type of sensitive data pattern
            
        Returns:
            Replacement string for redaction
        """
        replacements = {
            "EMAIL": "[EMAIL_REDACTED]",
            "PHONE": "[PHONE_REDACTED]",
            "SSN": "[SSN_REDACTED]",
            "CREDIT_CARD": "[CARD_REDACTED]",
            "IP_ADDRESS": "[IP_REDACTED]",
            "MEDICAL_RECORD": "[MEDICAL_ID_REDACTED]",
            "DIAGNOSIS": "[DIAGNOSIS_REDACTED]",
            "MEDICATION": "[MEDICATION_REDACTED]",
            "BANK_ACCOUNT": "[ACCOUNT_REDACTED]",
            "ROUTING_NUMBER": "[ROUTING_REDACTED]",
        }
        
        return replacements.get(pattern_type, "[REDACTED]")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get compliance engine performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            "total_checks": self._total_checks,
            "violations_found": self._violations_found,
            "violation_rate": (
                self._violations_found / max(self._total_checks, 1)
            ),
            "uptime_seconds": uptime,
            "checks_per_second": self._total_checks / max(uptime, 1),
            "policies_active": len(self.policy_manager.get_active_policies()),
            "detection_engines": len(self.detection_engine.engines),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on compliance engine components.
        
        Returns:
            Health check results
        """
        try:
            # Check policy manager
            policy_health = await self.policy_manager.health_check()
            
            # Check detection engine
            detection_health = await self.detection_engine.health_check()
            
            overall_status = "healthy"
            if (policy_health.get("status") != "healthy" or
                    detection_health.get("status") != "healthy"):
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "components": {
                    "policy_manager": policy_health,
                    "detection_engine": detection_health,
                },
                "metrics": self.get_metrics(),
            }
            
        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def reload_policies(self) -> None:
        """Reload compliance policies from configuration."""
        try:
            await self.policy_manager.reload_policies(
                self.config.compliance_policies
            )
            self.logger.info("Compliance policies reloaded successfully")
        except Exception as e:
            self.logger.error("Failed to reload policies", error=str(e))
            raise ConfigurationError(f"Policy reload failed: {str(e)}") from e