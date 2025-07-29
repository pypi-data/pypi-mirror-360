"""Policy management and enforcement for compliance checking.

This module provides policy management capabilities including policy loading,
evaluation, and enforcement for various compliance requirements.
"""

from typing import Any, Dict, List, Optional, Union

import structlog

from ..config import CompliancePolicy, ContentFilterPolicy, PIIPolicy
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


class PolicyManager:
    """Manager for compliance policies and their evaluation.
    
    This class handles policy loading, caching, and evaluation against
    requests and responses to determine compliance violations.
    
    Attributes:
        policies: Dictionary of loaded compliance policies
        logger: Structured logger
    """
    
    def __init__(self, policies: List[CompliancePolicy]) -> None:
        """Initialize the policy manager.
        
        Args:
            policies: List of compliance policies to manage
        """
        self.policies: Dict[str, CompliancePolicy] = {}
        self.logger = structlog.get_logger(__name__)
        
        # Load initial policies
        for policy in policies:
            self.policies[policy.name] = policy
        
        self.logger.info(
            "Policy manager initialized",
            policy_count=len(self.policies),
            active_policies=len(self.get_active_policies()),
        )
    
    async def evaluate_request(
        self,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ComplianceCheck]:
        """Evaluate request against all active policies.
        
        Args:
            request: Request to evaluate
            detection_results: Results from detection engines
            context: Optional context information
            
        Returns:
            List of compliance check results
        """
        context = context or {}
        compliance_checks = []
        
        for policy in self.get_active_policies():
            try:
                check = await self._evaluate_policy_for_request(
                    policy, request, detection_results, context
                )
                if check:
                    compliance_checks.append(check)
            except Exception as e:
                self.logger.error(
                    "Policy evaluation failed",
                    policy=policy.name,
                    error=str(e),
                )
                # Create a failure check
                compliance_checks.append(
                    ComplianceCheck(
                        policy_name=policy.name,
                        passed=False,
                        action=ComplianceAction.WARN,
                        severity=SeverityLevel.MEDIUM,
                        message=f"Policy evaluation failed: {str(e)}",
                    )
                )
        
        return compliance_checks
    
    async def evaluate_response(
        self,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ComplianceCheck]:
        """Evaluate response against all active policies.
        
        Args:
            response: Response to evaluate
            request: Original request
            detection_results: Results from detection engines
            context: Optional context information
            
        Returns:
            List of compliance check results
        """
        context = context or {}
        compliance_checks = []
        
        for policy in self.get_active_policies():
            try:
                check = await self._evaluate_policy_for_response(
                    policy, response, request, detection_results, context
                )
                if check:
                    compliance_checks.append(check)
            except Exception as e:
                self.logger.error(
                    "Policy evaluation failed",
                    policy=policy.name,
                    error=str(e),
                )
                # Create a failure check
                compliance_checks.append(
                    ComplianceCheck(
                        policy_name=policy.name,
                        passed=False,
                        action=ComplianceAction.WARN,
                        severity=SeverityLevel.MEDIUM,
                        message=f"Policy evaluation failed: {str(e)}",
                    )
                )
        
        return compliance_checks
    
    async def _evaluate_policy_for_request(
        self,
        policy: CompliancePolicy,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate a specific policy against a request.
        
        Args:
            policy: Policy to evaluate
            request: Request to check
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result or None if not applicable
        """
        if isinstance(policy, PIIPolicy):
            return await self._evaluate_pii_policy_request(
                policy, request, detection_results, context
            )
        elif isinstance(policy, ContentFilterPolicy):
            return await self._evaluate_content_filter_policy_request(
                policy, request, detection_results, context
            )
        else:
            # Generic policy evaluation
            return await self._evaluate_generic_policy_request(
                policy, request, detection_results, context
            )
    
    async def _evaluate_policy_for_response(
        self,
        policy: CompliancePolicy,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate a specific policy against a response.
        
        Args:
            policy: Policy to evaluate
            response: Response to check
            request: Original request
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result or None if not applicable
        """
        if isinstance(policy, PIIPolicy):
            return await self._evaluate_pii_policy_response(
                policy, response, request, detection_results, context
            )
        elif isinstance(policy, ContentFilterPolicy):
            return await self._evaluate_content_filter_policy_response(
                policy, response, request, detection_results, context
            )
        else:
            # Generic policy evaluation
            return await self._evaluate_generic_policy_response(
                policy, response, request, detection_results, context
            )
    
    async def _evaluate_pii_policy_request(
        self,
        policy: PIIPolicy,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate PII policy against request.
        
        Args:
            policy: PII policy to evaluate
            request: Request to check
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result
        """
        # Check for PII detections
        pii_results = detection_results.get("pii_detector", {})
        matches = pii_results.get("matches", [])
        
        # Filter matches by configured PII types
        relevant_matches = [
            match for match in matches
            if match.get("type", "").lower() in [
                pii_type.lower() for pii_type in policy.pii_types
            ]
        ]
        
        if not relevant_matches:
            return ComplianceCheck(
                policy_name=policy.name,
                passed=True,
                action=policy.action,
                severity=policy.severity,
                message="No PII detected in request",
            )
        
        # Check confidence threshold
        high_confidence_matches = [
            match for match in relevant_matches
            if match.get("confidence", 0.0) >= policy.detection_threshold
        ]
        
        if high_confidence_matches:
            pii_types = set(
                match.get("type") for match in high_confidence_matches
            )
            return ComplianceCheck(
                policy_name=policy.name,
                passed=False,
                action=policy.action,
                severity=policy.severity,
                message=f"PII detected in request: {', '.join(pii_types)}",
                details={
                    "matches": high_confidence_matches,
                    "pii_types": list(pii_types),
                    "match_count": len(high_confidence_matches),
                },
            )
        
        return ComplianceCheck(
            policy_name=policy.name,
            passed=True,
            action=policy.action,
            severity=policy.severity,
            message="PII detected but below confidence threshold",
            details={
                "matches": relevant_matches,
                "threshold": policy.detection_threshold,
            },
        )
    
    async def _evaluate_pii_policy_response(
        self,
        policy: PIIPolicy,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate PII policy against response.
        
        Args:
            policy: PII policy to evaluate
            response: Response to check
            request: Original request
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result
        """
        # Check for PII detections in response
        pii_results = detection_results.get("pii_detector", {})
        matches = pii_results.get("matches", [])
        
        # Filter matches by configured PII types
        relevant_matches = [
            match for match in matches
            if match.get("type", "").lower() in [
                pii_type.lower() for pii_type in policy.pii_types
            ]
        ]
        
        if not relevant_matches:
            return ComplianceCheck(
                policy_name=policy.name,
                passed=True,
                action=policy.action,
                severity=policy.severity,
                message="No PII detected in response",
            )
        
        # Check confidence threshold
        high_confidence_matches = [
            match for match in relevant_matches
            if match.get("confidence", 0.0) >= policy.detection_threshold
        ]
        
        if high_confidence_matches:
            pii_types = set(
                match.get("type") for match in high_confidence_matches
            )
            return ComplianceCheck(
                policy_name=policy.name,
                passed=False,
                action=policy.action,
                severity=policy.severity,
                message=f"PII detected in response: {', '.join(pii_types)}",
                details={
                    "matches": high_confidence_matches,
                    "pii_types": list(pii_types),
                    "match_count": len(high_confidence_matches),
                },
            )
        
        return ComplianceCheck(
            policy_name=policy.name,
            passed=True,
            action=policy.action,
            severity=policy.severity,
            message="PII detected but below confidence threshold",
            details={
                "matches": relevant_matches,
                "threshold": policy.detection_threshold,
            },
        )
    
    async def _evaluate_content_filter_policy_request(
        self,
        policy: ContentFilterPolicy,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate content filter policy against request.
        
        Args:
            policy: Content filter policy to evaluate
            request: Request to check
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result
        """
        # Check for harmful content detections
        violations = []
        
        for category in policy.filter_categories:
            category_results = detection_results.get(
                f"{category}_detector", {}
            )
            matches = category_results.get("matches", [])
            
            if matches:
                violations.extend([
                    {
                        "category": category,
                        "matches": matches,
                    }
                ])
        
        # Check custom patterns
        pattern_results = detection_results.get("pattern_detector", {})
        custom_matches = pattern_results.get("custom_matches", [])
        if custom_matches:
            violations.append({
                "category": "custom_patterns",
                "matches": custom_matches,
            })
        
        if not violations:
            return ComplianceCheck(
                policy_name=policy.name,
                passed=True,
                action=policy.action,
                severity=policy.severity,
                message="No harmful content detected in request",
            )
        
        # Determine severity based on violations
        violation_categories = [v["category"] for v in violations]
        
        return ComplianceCheck(
            policy_name=policy.name,
            passed=False,
            action=policy.action,
            severity=policy.severity,
            message=(
                f"Harmful content detected in request: "
                f"{', '.join(violation_categories)}"
            ),
            details={
                "violations": violations,
                "categories": violation_categories,
                "strictness_level": policy.strictness_level,
            },
        )
    
    async def _evaluate_content_filter_policy_response(
        self,
        policy: ContentFilterPolicy,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate content filter policy against response.
        
        Args:
            policy: Content filter policy to evaluate
            response: Response to check
            request: Original request
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result
        """
        # Similar to request evaluation but for response content
        violations = []
        
        for category in policy.filter_categories:
            category_results = detection_results.get(
                f"{category}_detector", {}
            )
            matches = category_results.get("matches", [])
            
            if matches:
                violations.extend([
                    {
                        "category": category,
                        "matches": matches,
                    }
                ])
        
        if not violations:
            return ComplianceCheck(
                policy_name=policy.name,
                passed=True,
                action=policy.action,
                severity=policy.severity,
                message="No harmful content detected in response",
            )
        
        violation_categories = [v["category"] for v in violations]
        
        return ComplianceCheck(
            policy_name=policy.name,
            passed=False,
            action=policy.action,
            severity=policy.severity,
            message=(
                f"Harmful content detected in response: "
                f"{', '.join(violation_categories)}"
            ),
            details={
                "violations": violations,
                "categories": violation_categories,
                "strictness_level": policy.strictness_level,
            },
        )
    
    async def _evaluate_generic_policy_request(
        self,
        policy: CompliancePolicy,
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate generic policy against request.
        
        Args:
            policy: Policy to evaluate
            request: Request to check
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result
        """
        # Default implementation for generic policies
        return ComplianceCheck(
            policy_name=policy.name,
            passed=True,
            action=policy.action,
            severity=policy.severity,
            message=f"Generic policy '{policy.name}' passed",
        )
    
    async def _evaluate_generic_policy_response(
        self,
        policy: CompliancePolicy,
        response: Union[ChatResponse, CompletionResponse, EmbeddingResponse],
        request: Union[ChatRequest, CompletionRequest, EmbeddingRequest],
        detection_results: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[ComplianceCheck]:
        """Evaluate generic policy against response.
        
        Args:
            policy: Policy to evaluate
            response: Response to check
            request: Original request
            detection_results: Detection engine results
            context: Context information
            
        Returns:
            Compliance check result
        """
        # Default implementation for generic policies
        return ComplianceCheck(
            policy_name=policy.name,
            passed=True,
            action=policy.action,
            severity=policy.severity,
            message=f"Generic policy '{policy.name}' passed",
        )
    
    def get_active_policies(self) -> List[CompliancePolicy]:
        """Get list of active policies.
        
        Returns:
            List of enabled compliance policies
        """
        return [policy for policy in self.policies.values() if policy.enabled]
    
    def get_policy(self, name: str) -> Optional[CompliancePolicy]:
        """Get policy by name.
        
        Args:
            name: Name of the policy
            
        Returns:
            Policy if found, None otherwise
        """
        return self.policies.get(name)
    
    def add_policy(self, policy: CompliancePolicy) -> None:
        """Add or update a policy.
        
        Args:
            policy: Policy to add or update
        """
        self.policies[policy.name] = policy
        self.logger.info("Policy added/updated", policy_name=policy.name)
    
    def remove_policy(self, name: str) -> bool:
        """Remove a policy by name.
        
        Args:
            name: Name of the policy to remove
            
        Returns:
            True if policy was removed, False if not found
        """
        if name in self.policies:
            del self.policies[name]
            self.logger.info("Policy removed", policy_name=name)
            return True
        return False
    
    async def reload_policies(
        self, policies: List[CompliancePolicy]
    ) -> None:
        """Reload policies from new configuration.
        
        Args:
            policies: New list of policies to load
        """
        old_count = len(self.policies)
        self.policies.clear()
        
        for policy in policies:
            self.policies[policy.name] = policy
        
        self.logger.info(
            "Policies reloaded",
            old_count=old_count,
            new_count=len(self.policies),
            active_count=len(self.get_active_policies()),
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on policy manager.
        
        Returns:
            Health check results
        """
        try:
            active_policies = self.get_active_policies()
            
            return {
                "status": "healthy",
                "policy_count": len(self.policies),
                "active_policies": len(active_policies),
                "policy_types": {
                    "pii": len([
                        p for p in active_policies
                        if isinstance(p, PIIPolicy)
                    ]),
                    "content_filter": len([
                        p for p in active_policies
                        if isinstance(p, ContentFilterPolicy)
                    ]),
                    "generic": len([
                        p for p in active_policies
                        if not isinstance(p, (PIIPolicy, ContentFilterPolicy))
                    ]),
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }