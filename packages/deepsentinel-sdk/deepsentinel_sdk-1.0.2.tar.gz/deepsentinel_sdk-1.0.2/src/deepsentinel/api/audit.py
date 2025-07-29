"""Audit API endpoints for DeepSentinel services.

This module provides specialized API client functionality for audit logging,
event tracking, and compliance audit trail management.
"""

from typing import Any, Dict, List, Optional

import structlog

from .client import DeepSentinelAPIClient


class AuditAPI:
    """Audit API client for DeepSentinel services.
    
    This class provides specialized methods for managing audit logs,
    tracking events, and retrieving compliance audit trails.
    
    Attributes:
        client: Base API client
        logger: Structured logger
    """
    
    def __init__(self, client: DeepSentinelAPIClient) -> None:
        """Initialize the audit API client.
        
        Args:
            client: Base API client instance
        """
        self.client = client
        self.logger = structlog.get_logger(__name__)
    
    async def log_event(
        self, event_data: Dict[str, Any], sync: bool = False
    ) -> Dict[str, Any]:
        """Log an audit event to the audit trail.
        
        Args:
            event_data: Audit event data
            sync: Whether to wait for log confirmation
            
        Returns:
            Log confirmation or acknowledgment
        """
        params = {"sync": "true" if sync else "false"}
        return await self.client.post(
            "audit/events", data=event_data, params=params
        )
    
    async def log_batch_events(
        self, events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Log multiple audit events in batch.
        
        Args:
            events: List of audit event data
            
        Returns:
            Batch log confirmation
        """
        payload = {"events": events}
        return await self.client.post("audit/events/batch", data=payload)
    
    async def get_events(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "timestamp:desc",
    ) -> Dict[str, Any]:
        """Get audit events filtered by criteria.
        
        Args:
            start_time: ISO timestamp for earliest events
            end_time: ISO timestamp for latest events
            user_id: Filter by user ID
            session_id: Filter by session ID
            event_types: Filter by event types
            limit: Maximum number of events to return
            offset: Offset for pagination
            sort: Sorting field and direction
            
        Returns:
            Filtered audit events
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "sort": sort,
        }
        
        if start_time:
            params["start_time"] = start_time
        
        if end_time:
            params["end_time"] = end_time
        
        if user_id:
            params["user_id"] = user_id
        
        if session_id:
            params["session_id"] = session_id
        
        if event_types:
            params["event_types"] = ",".join(event_types)
        
        return await self.client.get("audit/events", params=params)
    
    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get details for a specific audit event.
        
        Args:
            event_id: ID of the audit event
            
        Returns:
            Audit event details
        """
        return await self.client.get(f"audit/events/{event_id}")
    
    async def search_events(
        self, query: str, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """Search audit events with a query string.
        
        Args:
            query: Search query string
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            Search results
        """
        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
        }
        
        return await self.client.get("audit/events/search", params=params)
    
    async def get_user_activity(
        self, user_id: str, limit: int = 100
    ) -> Dict[str, Any]:
        """Get activity history for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of events to return
            
        Returns:
            User activity history
        """
        params = {
            "user_id": user_id,
            "limit": limit,
        }
        
        return await self.client.get("audit/activity/user", params=params)
    
    async def get_session_activity(
        self, session_id: str
    ) -> Dict[str, Any]:
        """Get activity history for a specific session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session activity history
        """
        params = {"session_id": session_id}
        return await self.client.get("audit/activity/session", params=params)
    
    async def get_audit_trail_summary(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get summary statistics for the audit trail.
        
        Args:
            start_time: ISO timestamp for earliest events
            end_time: ISO timestamp for latest events
            
        Returns:
            Audit trail summary statistics
        """
        params = {}
        
        if start_time:
            params["start_time"] = start_time
        
        if end_time:
            params["end_time"] = end_time
        
        return await self.client.get("audit/summary", params=params)
    
    async def export_audit_logs(
        self,
        start_time: str,
        end_time: str,
        format: str = "json",
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Export audit logs for a specified time period.
        
        Args:
            start_time: ISO timestamp for earliest events
            end_time: ISO timestamp for latest events
            format: Export format (json, csv)
            filters: Optional filters to apply
            
        Returns:
            Export details including download URL
        """
        payload = {
            "start_time": start_time,
            "end_time": end_time,
            "format": format,
        }
        
        if filters:
            payload["filters"] = filters
        
        return await self.client.post("audit/export", data=payload)
    
    async def get_compliance_violations(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get compliance violations from audit trail.
        
        Args:
            start_time: ISO timestamp for earliest violations
            end_time: ISO timestamp for latest violations
            severity: Filter by severity level
            limit: Maximum number of violations to return
            offset: Offset for pagination
            
        Returns:
            Compliance violations
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        
        if start_time:
            params["start_time"] = start_time
        
        if end_time:
            params["end_time"] = end_time
        
        if severity:
            params["severity"] = severity
        
        return await self.client.get("audit/violations", params=params)
    
    async def get_audit_settings(self) -> Dict[str, Any]:
        """Get current audit settings and configuration.
        
        Returns:
            Audit settings
        """
        return await self.client.get("audit/settings")
    
    async def update_audit_settings(
        self, settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update audit settings and configuration.
        
        Args:
            settings: Updated settings data
            
        Returns:
            Updated audit settings
        """
        return await self.client.put("audit/settings", data=settings)
    
    async def purge_audit_logs(
        self,
        older_than: str,
        event_types: Optional[List[str]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Purge audit logs older than specified time.
        
        Args:
            older_than: ISO timestamp or duration (e.g. "90d")
            event_types: Optional event types to purge
            dry_run: Only simulate purge and return stats
            
        Returns:
            Purge operation results
        """
        payload = {
            "older_than": older_than,
            "dry_run": dry_run,
        }
        
        if event_types:
            payload["event_types"] = event_types
        
        return await self.client.post("audit/purge", data=payload)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check audit API service health.
        
        Returns:
            Health check results
        """
        return await self.client.get("audit/health")