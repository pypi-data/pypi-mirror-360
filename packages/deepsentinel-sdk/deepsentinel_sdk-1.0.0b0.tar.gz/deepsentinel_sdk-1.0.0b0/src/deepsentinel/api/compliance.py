"""Compliance API endpoints for DeepSentinel services.

This module provides specialized API client functionality for compliance
validation, policy management, and content scanning services.
"""

from typing import Any, Dict, List, Optional

import structlog

from .client import DeepSentinelAPIClient


class ComplianceAPI:
    """Compliance API client for DeepSentinel services.
    
    This class provides specialized methods for compliance validation,
    policy management, and content scanning services.
    
    Attributes:
        client: Base API client
        logger: Structured logger
    """
    
    def __init__(self, client: DeepSentinelAPIClient) -> None:
        """Initialize the compliance API client.
        
        Args:
            client: Base API client instance
        """
        self.client = client
        self.logger = structlog.get_logger(__name__)
    
    async def validate_text(
        self,
        text: str,
        policy_ids: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate text content against compliance policies.
        
        Args:
            text: Text content to validate
            policy_ids: Optional list of specific policy IDs to check
            context: Optional context information
            
        Returns:
            Validation results
        """
        payload = {
            "content": text,
            "content_type": "text/plain",
        }
        
        if policy_ids:
            payload["policy_ids"] = policy_ids
        
        if context:
            payload["context"] = context
        
        return await self.client.post("compliance/validate", data=payload)
    
    async def scan_for_sensitive_data(
        self,
        content: str,
        content_type: str = "text/plain",
        sensitivity: str = "medium",
        types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Scan content for sensitive data patterns.
        
        Args:
            content: Content to scan
            content_type: MIME type of content
            sensitivity: Scanning sensitivity (low, medium, high)
            types: Optional list of data types to scan for
            
        Returns:
            Scanning results
        """
        payload = {
            "content": content,
            "content_type": content_type,
            "sensitivity": sensitivity,
        }
        
        if types:
            payload["types"] = types
        
        return await self.client.post("compliance/scan", data=payload)
    
    async def redact_sensitive_data(
        self,
        content: str,
        content_type: str = "text/plain",
        types: Optional[List[str]] = None,
        replacement: str = "[REDACTED]",
    ) -> Dict[str, Any]:
        """Redact sensitive data from content.
        
        Args:
            content: Content to redact
            content_type: MIME type of content
            types: Optional list of data types to redact
            replacement: Replacement string for redacted content
            
        Returns:
            Redaction results with redacted content
        """
        payload = {
            "content": content,
            "content_type": content_type,
            "replacement": replacement,
        }
        
        if types:
            payload["types"] = types
        
        return await self.client.post("compliance/redact", data=payload)
    
    async def validate_request(
        self,
        request_data: Dict[str, Any],
        request_type: str,
        policy_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Validate a request against compliance policies.
        
        Args:
            request_data: Request data to validate
            request_type: Type of request (chat, completion, embedding)
            policy_ids: Optional list of specific policy IDs to check
            
        Returns:
            Validation results
        """
        payload = {
            "request_data": request_data,
            "request_type": request_type,
        }
        
        if policy_ids:
            payload["policy_ids"] = policy_ids
        
        return await self.client.post(
            "compliance/validate/request", data=payload
        )
    
    async def validate_response(
        self,
        response_data: Dict[str, Any],
        request_data: Dict[str, Any],
        response_type: str,
        policy_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Validate a response against compliance policies.
        
        Args:
            response_data: Response data to validate
            request_data: Original request data
            response_type: Type of response (chat, completion, embedding)
            policy_ids: Optional list of specific policy IDs to check
            
        Returns:
            Validation results
        """
        payload = {
            "response_data": response_data,
            "request_data": request_data,
            "response_type": response_type,
        }
        
        if policy_ids:
            payload["policy_ids"] = policy_ids
        
        return await self.client.post(
            "compliance/validate/response", data=payload
        )
    
    async def get_policies(
        self, active_only: bool = True
    ) -> Dict[str, Any]:
        """Get available compliance policies.
        
        Args:
            active_only: Only return active policies
            
        Returns:
            List of available policies
        """
        params = {"active_only": "true" if active_only else "false"}
        return await self.client.get("compliance/policies", params=params)
    
    async def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get details for a specific compliance policy.
        
        Args:
            policy_id: ID of the policy
            
        Returns:
            Policy details
        """
        return await self.client.get(f"compliance/policies/{policy_id}")
    
    async def create_custom_policy(
        self, policy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a custom compliance policy.
        
        Args:
            policy_data: Policy configuration data
            
        Returns:
            Created policy details
        """
        return await self.client.post(
            "compliance/policies/custom", data=policy_data
        )
    
    async def update_custom_policy(
        self, policy_id: str, policy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a custom compliance policy.
        
        Args:
            policy_id: ID of the policy to update
            policy_data: Updated policy configuration data
            
        Returns:
            Updated policy details
        """
        return await self.client.put(
            f"compliance/policies/custom/{policy_id}", data=policy_data
        )
    
    async def delete_custom_policy(self, policy_id: str) -> Dict[str, Any]:
        """Delete a custom compliance policy.
        
        Args:
            policy_id: ID of the policy to delete
            
        Returns:
            Deletion result
        """
        return await self.client.delete(
            f"compliance/policies/custom/{policy_id}"
        )
    
    async def get_detection_patterns(
        self, pattern_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get available detection patterns.
        
        Args:
            pattern_type: Optional type of patterns to filter by
            
        Returns:
            List of detection patterns
        """
        params = {}
        if pattern_type:
            params["type"] = pattern_type
        
        return await self.client.get("compliance/patterns", params=params)
    
    async def create_custom_pattern(
        self, pattern_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a custom detection pattern.
        
        Args:
            pattern_data: Pattern configuration data
            
        Returns:
            Created pattern details
        """
        return await self.client.post(
            "compliance/patterns/custom", data=pattern_data
        )
    
    async def get_compliance_report(
        self,
        start_date: str,
        end_date: str,
        report_type: str = "summary",
    ) -> Dict[str, Any]:
        """Get a compliance report for a specified time period.
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            report_type: Type of report (summary, detailed)
            
        Returns:
            Compliance report data
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "type": report_type,
        }
        
        return await self.client.get("compliance/reports", params=params)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check compliance API service health.
        
        Returns:
            Health check results
        """
        return await self.client.get("compliance/health")