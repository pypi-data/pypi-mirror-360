"""Performance metrics collection and monitoring.

This module provides comprehensive metrics collection for tracking request
performance, token usage, cache effectiveness, and system health.
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog


@dataclass
class PerformanceMetrics:
    """Performance metrics for requests and operations.
    
    Attributes:
        request_count: Total number of requests
        successful_requests: Number of successful requests
        failed_requests: Number of failed requests
        total_duration: Total time spent on requests
        avg_duration: Average request duration
        min_duration: Minimum request duration
        max_duration: Maximum request duration
        retry_count: Total number of retries
        rate_limit_hits: Number of rate limit encounters
    """
    
    request_count: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    retry_count: int = 0
    rate_limit_hits: int = 0
    
    def update_duration(self, duration: float) -> None:
        """Update duration statistics."""
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        if self.request_count > 0:
            self.avg_duration = self.total_duration / self.request_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "request_count": self.request_count,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_duration": self.total_duration,
            "avg_duration": self.avg_duration,
            "min_duration": (
                self.min_duration if self.min_duration != float('inf') else 0.0
            ),
            "max_duration": self.max_duration,
            "retry_count": self.retry_count,
            "rate_limit_hits": self.rate_limit_hits,
            "success_rate": (
                self.successful_requests / self.request_count
                if self.request_count > 0 else 0.0
            ),
        }


@dataclass
class TokenUsageMetrics:
    """Token usage tracking metrics.
    
    Attributes:
        total_tokens: Total tokens used
        prompt_tokens: Tokens used for prompts
        completion_tokens: Tokens used for completions
        total_cost: Estimated total cost
        requests_with_tokens: Number of requests that used tokens
    """
    
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    requests_with_tokens: int = 0
    
    def add_usage(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: Optional[int] = None,
        cost: float = 0.0,
    ) -> None:
        """Add token usage data."""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        
        if total_tokens is not None:
            self.total_tokens += total_tokens
        else:
            self.total_tokens += prompt_tokens + completion_tokens
        
        self.total_cost += cost
        self.requests_with_tokens += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_cost": self.total_cost,
            "requests_with_tokens": self.requests_with_tokens,
            "avg_tokens_per_request": (
                self.total_tokens / self.requests_with_tokens
                if self.requests_with_tokens > 0 else 0.0
            ),
            "avg_cost_per_request": (
                self.total_cost / self.requests_with_tokens
                if self.requests_with_tokens > 0 else 0.0
            ),
        }


@dataclass
class CacheMetrics:
    """Cache performance metrics.
    
    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        evictions: Number of cache evictions
        expired: Number of expired entries
        size: Current cache size
        max_size: Maximum cache size
    """
    
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired: int = 0
    size: int = 0
    max_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expired": self.expired,
            "size": self.size,
            "max_size": self.max_size,
            "hit_rate": self.hit_rate,
            "miss_rate": self.miss_rate,
            "utilization": (
                self.size / self.max_size if self.max_size > 0 else 0.0
            ),
        }


class MetricsCollector:
    """Comprehensive metrics collector for SDK performance monitoring.
    
    This class collects and aggregates performance metrics including:
    - Request performance and timing
    - Token usage and costs
    - Cache effectiveness
    - Provider-specific metrics
    - System health indicators
    
    Attributes:
        enabled: Whether metrics collection is enabled
        window_size: Size of the rolling window for metrics
        logger: Structured logger
    """
    
    def __init__(
        self,
        enabled: bool = True,
        window_size: int = 1000,
        retention_minutes: int = 60,
    ) -> None:
        """Initialize the metrics collector.
        
        Args:
            enabled: Whether to collect metrics
            window_size: Size of rolling window for recent metrics
            retention_minutes: How long to retain detailed metrics
        """
        self.enabled = enabled
        self.window_size = window_size
        self.retention_minutes = retention_minutes
        
        # Overall metrics
        self._performance_metrics = PerformanceMetrics()
        self._token_metrics = TokenUsageMetrics()
        self._cache_metrics = CacheMetrics()
        
        # Provider-specific metrics
        self._provider_metrics: Dict[str, PerformanceMetrics] = defaultdict(
            PerformanceMetrics
        )
        self._provider_tokens: Dict[str, TokenUsageMetrics] = defaultdict(
            TokenUsageMetrics
        )
        
        # Operation-specific metrics
        self._operation_metrics: Dict[str, PerformanceMetrics] = defaultdict(
            PerformanceMetrics
        )
        
        # Rolling window for recent data
        self._recent_requests: deque = deque(maxlen=window_size)
        self._recent_errors: deque = deque(maxlen=window_size)
        
        # Time series data for trending
        self._hourly_stats: Dict[int, Dict[str, Any]] = {}
        
        self.logger = structlog.get_logger(__name__)
        self._start_time = time.time()
        
        # Start background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        if enabled:
            self._start_cleanup_task()
    
    def _start_cleanup_task(self) -> None:
        """Start background cleanup task for old metrics."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(
                self._cleanup_old_metrics()
            )
    
    async def _cleanup_old_metrics(self) -> None:
        """Background task to clean up old metrics data."""
        while self.enabled:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up old hourly stats
                current_hour = int(time.time()) // 3600
                cutoff_hour = current_hour - self.retention_minutes // 60
                
                old_hours = [
                    hour for hour in self._hourly_stats.keys()
                    if hour < cutoff_hour
                ]
                
                for hour in old_hours:
                    del self._hourly_stats[hour]
                
                if old_hours:
                    self.logger.debug(
                        "Cleaned up old metrics",
                        removed_hours=len(old_hours)
                    )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Metrics cleanup error", error=str(e))
    
    def record_request(
        self,
        provider: str,
        operation: str,
        duration: float,
        success: bool,
        retry_count: int = 0,
        rate_limited: bool = False,
        error: Optional[str] = None,
    ) -> None:
        """Record a request performance metric.
        
        Args:
            provider: Provider name
            operation: Operation type (chat, completion, etc.)
            duration: Request duration in seconds
            success: Whether the request was successful
            retry_count: Number of retries performed
            rate_limited: Whether rate limiting was encountered
            error: Error message if request failed
        """
        if not self.enabled:
            return
        
        timestamp = time.time()
        
        # Update overall metrics
        self._performance_metrics.request_count += 1
        self._performance_metrics.update_duration(duration)
        self._performance_metrics.retry_count += retry_count
        
        if success:
            self._performance_metrics.successful_requests += 1
        else:
            self._performance_metrics.failed_requests += 1
        
        if rate_limited:
            self._performance_metrics.rate_limit_hits += 1
        
        # Update provider-specific metrics
        provider_metrics = self._provider_metrics[provider]
        provider_metrics.request_count += 1
        provider_metrics.update_duration(duration)
        provider_metrics.retry_count += retry_count
        
        if success:
            provider_metrics.successful_requests += 1
        else:
            provider_metrics.failed_requests += 1
        
        if rate_limited:
            provider_metrics.rate_limit_hits += 1
        
        # Update operation-specific metrics
        operation_metrics = self._operation_metrics[operation]
        operation_metrics.request_count += 1
        operation_metrics.update_duration(duration)
        
        if success:
            operation_metrics.successful_requests += 1
        else:
            operation_metrics.failed_requests += 1
        
        # Add to rolling window
        request_data = {
            "timestamp": timestamp,
            "provider": provider,
            "operation": operation,
            "duration": duration,
            "success": success,
            "retry_count": retry_count,
            "rate_limited": rate_limited,
        }
        self._recent_requests.append(request_data)
        
        # Track errors
        if not success and error:
            error_data = {
                "timestamp": timestamp,
                "provider": provider,
                "operation": operation,
                "error": error,
            }
            self._recent_errors.append(error_data)
        
        # Update hourly stats
        self._update_hourly_stats(timestamp, provider, operation, success)
    
    def record_token_usage(
        self,
        provider: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: Optional[int] = None,
        cost: float = 0.0,
    ) -> None:
        """Record token usage metrics.
        
        Args:
            provider: Provider name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            total_tokens: Total tokens (if different from sum)
            cost: Estimated cost for this usage
        """
        if not self.enabled:
            return
        
        # Update overall token metrics
        self._token_metrics.add_usage(
            prompt_tokens, completion_tokens, total_tokens, cost
        )
        
        # Update provider-specific token metrics
        self._provider_tokens[provider].add_usage(
            prompt_tokens, completion_tokens, total_tokens, cost
        )
    
    def record_cache_metrics(
        self,
        hits: int = 0,
        misses: int = 0,
        evictions: int = 0,
        expired: int = 0,
        current_size: int = 0,
        max_size: int = 0,
    ) -> None:
        """Record cache performance metrics.
        
        Args:
            hits: Number of cache hits
            misses: Number of cache misses
            evictions: Number of evictions
            expired: Number of expired entries
            current_size: Current cache size
            max_size: Maximum cache size
        """
        if not self.enabled:
            return
        
        self._cache_metrics.hits += hits
        self._cache_metrics.misses += misses
        self._cache_metrics.evictions += evictions
        self._cache_metrics.expired += expired
        self._cache_metrics.size = current_size
        self._cache_metrics.max_size = max_size
    
    def _update_hourly_stats(
        self,
        timestamp: float,
        provider: str,
        operation: str,
        success: bool,
    ) -> None:
        """Update hourly statistics for trending."""
        hour = int(timestamp) // 3600
        
        if hour not in self._hourly_stats:
            self._hourly_stats[hour] = {
                "timestamp": hour * 3600,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "providers": defaultdict(int),
                "operations": defaultdict(int),
            }
        
        stats = self._hourly_stats[hour]
        stats["total_requests"] += 1
        
        if success:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
        
        stats["providers"][provider] += 1
        stats["operations"][operation] += 1
    
    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall performance metrics.
        
        Returns:
            Dictionary containing overall metrics
        """
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "performance": self._performance_metrics.to_dict(),
            "tokens": self._token_metrics.to_dict(),
            "cache": self._cache_metrics.to_dict(),
            "recent_requests": len(self._recent_requests),
            "recent_errors": len(self._recent_errors),
        }
    
    def get_provider_metrics(
        self, provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get provider-specific metrics.
        
        Args:
            provider: Specific provider name (returns all if None)
            
        Returns:
            Dictionary containing provider metrics
        """
        if provider:
            return {
                "performance": self._provider_metrics[provider].to_dict(),
                "tokens": self._provider_tokens[provider].to_dict(),
            }
        
        result = {}
        provider_keys = set(self._provider_metrics.keys())
        token_keys = set(self._provider_tokens.keys())
        for prov in provider_keys | token_keys:
            result[prov] = {
                "performance": self._provider_metrics[prov].to_dict(),
                "tokens": self._provider_tokens[prov].to_dict(),
            }
        
        return result
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation-specific metrics.
        
        Returns:
            Dictionary containing operation metrics
        """
        return {
            operation: metrics.to_dict()
            for operation, metrics in self._operation_metrics.items()
        }
    
    def get_recent_requests(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get recent request data.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of recent request data
        """
        requests = list(self._recent_requests)
        if limit:
            requests = requests[-limit:]
        return requests
    
    def get_recent_errors(
        self, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get recent error data.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error data
        """
        errors = list(self._recent_errors)
        if limit:
            errors = errors[-limit:]
        return errors
    
    def get_hourly_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get hourly trend data.
        
        Args:
            hours: Number of hours of data to return
            
        Returns:
            List of hourly statistics
        """
        current_hour = int(time.time()) // 3600
        start_hour = current_hour - hours
        
        result = []
        for hour in range(start_hour, current_hour + 1):
            if hour in self._hourly_stats:
                stats = self._hourly_stats[hour].copy()
                # Convert defaultdicts to regular dicts
                stats["providers"] = dict(stats["providers"])
                stats["operations"] = dict(stats["operations"])
                result.append(stats)
            else:
                # Fill in missing hours with zeros
                result.append({
                    "timestamp": hour * 3600,
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "providers": {},
                    "operations": {},
                })
        
        return result
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive metrics report.
        
        Returns:
            Dictionary containing comprehensive metrics report
        """
        return {
            "timestamp": time.time(),
            "overall": self.get_overall_metrics(),
            "providers": self.get_provider_metrics(),
            "operations": self.get_operation_metrics(),
            "recent_performance": {
                "requests": len(self._recent_requests),
                "errors": len(self._recent_errors),
                "avg_duration_last_100": self._calculate_recent_avg_duration(),
                "error_rate_last_100": self._calculate_recent_error_rate(),
            },
            "trends": self.get_hourly_trends(24),
        }
    
    def _calculate_recent_avg_duration(self) -> float:
        """Calculate average duration for recent requests."""
        if not self._recent_requests:
            return 0.0
        
        recent_100 = list(self._recent_requests)[-100:]
        total_duration = sum(req["duration"] for req in recent_100)
        return total_duration / len(recent_100)
    
    def _calculate_recent_error_rate(self) -> float:
        """Calculate error rate for recent requests."""
        if not self._recent_requests:
            return 0.0
        
        recent_100 = list(self._recent_requests)[-100:]
        failed_count = sum(1 for req in recent_100 if not req["success"])
        return failed_count / len(recent_100)
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self._performance_metrics = PerformanceMetrics()
        self._token_metrics = TokenUsageMetrics()
        self._cache_metrics = CacheMetrics()
        self._provider_metrics.clear()
        self._provider_tokens.clear()
        self._operation_metrics.clear()
        self._recent_requests.clear()
        self._recent_errors.clear()
        self._hourly_stats.clear()
        self._start_time = time.time()
        
        self.logger.info("Metrics reset")
    
    async def close(self) -> None:
        """Close the metrics collector and cleanup resources."""
        self.enabled = False
        
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Metrics collector closed")