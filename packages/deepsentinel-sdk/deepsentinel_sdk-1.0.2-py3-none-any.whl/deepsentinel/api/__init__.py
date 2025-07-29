"""API client for DeepSentinel compliance services.

This package provides client interfaces for interacting with DeepSentinel's
compliance, audit, and API services.
"""

from .client import DeepSentinelAPIClient
from .compliance import ComplianceAPI
from .audit import AuditAPI

__all__ = [
    "DeepSentinelAPIClient",
    "ComplianceAPI",
    "AuditAPI",
]