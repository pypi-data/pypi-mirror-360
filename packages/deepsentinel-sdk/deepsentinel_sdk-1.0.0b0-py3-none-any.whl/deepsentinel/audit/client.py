"""Audit client for DeepSentinel SDK.

This module implements the audit client that handles audit event logging,
storage backends, batch processing, and performance metrics collection.
"""

import asyncio
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, Union

import aiofiles
import aiohttp
import structlog

from ..config import AuditConfig
from ..metrics.collector import MetricsCollector
from ..types import AuditEntry
from .events import AuditEvent, OperationMetrics, create_system_error_event


class AuditStorage(ABC):
    """Abstract base class for audit storage backends.
    
    This class defines the interface that all storage backends must implement
    for storing and retrieving audit events.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the storage backend.
        
        This method should be called before using the storage backend.
        It should set up any necessary resources (e.g., connections, files).
        """
        pass
    
    @abstractmethod
    async def store_event(self, event: AuditEvent) -> None:
        """Store a single audit event.
        
        Args:
            event: The audit event to store
        """
        pass
    
    @abstractmethod
    async def store_events(self, events: List[AuditEvent]) -> None:
        """Store multiple audit events in batch.
        
        Args:
            events: List of audit events to store
        """
        pass
    
    @abstractmethod
    async def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Retrieve audit events based on criteria.
        
        Args:
            start_time: Optional start time for filtering events
            end_time: Optional end time for filtering events
            filters: Optional additional filters
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of matching audit events
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources used by the storage backend.
        
        This method should be called when the storage backend is no longer needed.
        It should release any resources (e.g., connections, files).
        """
        pass


class FileAuditStorage(AuditStorage):
    """File-based storage backend for audit events.
    
    This class implements storage of audit events in local files,
    supporting both JSON and JSONL formats with rotation capabilities.
    
    Attributes:
        config: Audit configuration
        log_dir: Directory for audit log files
        file_format: Format of audit log files ("json" or "jsonl")
        max_file_size_mb: Maximum file size before rotation
        file_rotation_count: Number of files to keep during rotation
        current_file: Path to the current audit log file
        logger: Structured logger
    """
    
    def __init__(
        self,
        config: AuditConfig,
        log_dir: Optional[str] = None,
        file_format: str = "jsonl",
        max_file_size_mb: int = 10,
        file_rotation_count: int = 5,
    ) -> None:
        """Initialize file-based audit storage.
        
        Args:
            config: Audit configuration
            log_dir: Directory for audit log files (default: ./audit_logs)
            file_format: Format of audit log files ("json" or "jsonl")
            max_file_size_mb: Maximum file size before rotation (in MB)
            file_rotation_count: Number of files to keep during rotation
        """
        self.config = config
        self.log_dir = Path(log_dir or "./audit_logs")
        self.file_format = file_format.lower()
        self.max_file_size_mb = max_file_size_mb
        self.file_rotation_count = file_rotation_count
        self.current_file: Optional[Path] = None
        self.logger = structlog.get_logger(__name__)
        
        # File write lock to prevent concurrent writes
        self._file_lock = asyncio.Lock()
        
        if self.file_format not in ["json", "jsonl"]:
            raise ValueError(
                f"Invalid file format: {file_format}. "
                f"Supported formats: json, jsonl"
            )
    
    async def initialize(self) -> None:
        """Initialize the file storage backend."""
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Set current file path
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        self.current_file = self.log_dir / f"audit_{timestamp}.{self.file_format}"
        
        # Create empty file if it doesn't exist
        if not self.current_file.exists():
            if self.file_format == "json":
                async with aiofiles.open(
                    self.current_file, "w", encoding="utf-8"
                ) as f:
                    await f.write("[]")
            else:
                # For JSONL, no header is needed
                async with aiofiles.open(
                    self.current_file, "w", encoding="utf-8"
                ) as f:
                    pass
    
    async def _check_rotation(self) -> None:
        """Check if file rotation is needed and rotate if necessary."""
        if not self.current_file or not self.current_file.exists():
            return
            
        # Check file size
        file_size_mb = self.current_file.stat().st_size / (1024 * 1024)
        if file_size_mb < self.max_file_size_mb:
            return
            
        # Rotate files
        await self._rotate_files()
    
    async def _rotate_files(self) -> None:
        """Rotate audit log files."""
        if not self.current_file:
            return
            
        # Determine timestamp for new file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create new file name
        new_file = self.log_dir / f"audit_{timestamp}.{self.file_format}"
        
        # Move current file to new file
        self.current_file.rename(new_file)
        
        # Create new current file
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        self.current_file = self.log_dir / f"audit_{timestamp}.{self.file_format}"
        
        if self.file_format == "json":
            async with aiofiles.open(
                self.current_file, "w", encoding="utf-8"
            ) as f:
                await f.write("[]")
        
        # Delete old files if needed
        await self._cleanup_old_files()
    
    async def _cleanup_old_files(self) -> None:
        """Remove old audit log files based on rotation count."""
        # Get all audit log files
        files = list(self.log_dir.glob(f"audit_*.{self.file_format}"))
        
        # Sort files by modification time (newest first)
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove oldest files beyond rotation count
        if len(files) > self.file_rotation_count:
            for old_file in files[self.file_rotation_count:]:
                try:
                    old_file.unlink()
                except Exception as e:
                    self.logger.warning(
                        "Failed to delete old audit log file",
                        file=str(old_file),
                        error=str(e),
                    )
    
    async def store_event(self, event: AuditEvent) -> None:
        """Store a single audit event in the file.
        
        Args:
            event: Audit event to store
        """
        if not self.current_file:
            await self.initialize()
            
        async with self._file_lock:
            await self._check_rotation()
            
            # Convert event to dict for storage
            event_dict = event.to_dict()
            
            if self.file_format == "json":
                # Load existing events
                async with aiofiles.open(
                    self.current_file, "r", encoding="utf-8"
                ) as f:
                    content = await f.read()
                    events = json.loads(content)
                    
                # Add new event
                events.append(event_dict)
                
                # Write back all events
                async with aiofiles.open(
                    self.current_file, "w", encoding="utf-8"
                ) as f:
                    await f.write(json.dumps(events, indent=2))
            else:
                # For JSONL, simply append the new event
                async with aiofiles.open(
                    self.current_file, "a", encoding="utf-8"
                ) as f:
                    await f.write(json.dumps(event_dict) + "\n")
    
    async def store_events(self, events: List[AuditEvent]) -> None:
        """Store multiple audit events in batch.
        
        Args:
            events: List of audit events to store
        """
        if not events:
            return
            
        if not self.current_file:
            await self.initialize()
            
        async with self._file_lock:
            await self._check_rotation()
            
            # Convert events to dicts for storage
            event_dicts = [event.to_dict() for event in events]
            
            if self.file_format == "json":
                # Load existing events
                async with aiofiles.open(
                    self.current_file, "r", encoding="utf-8"
                ) as f:
                    content = await f.read()
                    existing_events = json.loads(content)
                    
                # Add new events
                existing_events.extend(event_dicts)
                
                # Write back all events
                async with aiofiles.open(
                    self.current_file, "w", encoding="utf-8"
                ) as f:
                    await f.write(json.dumps(existing_events, indent=2))
            else:
                # For JSONL, append all new events
                async with aiofiles.open(
                    self.current_file, "a", encoding="utf-8"
                ) as f:
                    for event_dict in event_dicts:
                        await f.write(json.dumps(event_dict) + "\n")
    
    async def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Retrieve audit events based on criteria.
        
        Args:
            start_time: Optional start time for filtering events
            end_time: Optional end time for filtering events
            filters: Optional additional filters
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of matching audit events
        """
        if not self.current_file or not self.current_file.exists():
            return []
            
        events = []
        
        # Process current file
        if self.file_format == "json":
            # Load all events from JSON file
            async with aiofiles.open(
                self.current_file, "r", encoding="utf-8"
            ) as f:
                content = await f.read()
                file_events = json.loads(content)
                events.extend(file_events)
        else:
            # Load events from JSONL file
            async with aiofiles.open(
                self.current_file, "r", encoding="utf-8"
            ) as f:
                async for line in f:
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError:
                            self.logger.warning(
                                "Failed to parse audit event", line=line
                            )
        
        # Apply filters
        filtered_events = []
        for event in events:
            # Parse timestamp if needed
            if isinstance(event.get("timestamp"), str):
                try:
                    event_time = datetime.fromisoformat(
                        event["timestamp"].rstrip("Z")
                    )
                except ValueError:
                    # Skip events with invalid timestamp
                    continue
            else:
                event_time = event.get("timestamp")
                
            # Apply time filters
            if start_time and (not event_time or event_time < start_time):
                continue
                
            if end_time and (not event_time or event_time > end_time):
                continue
                
            # Apply additional filters
            if filters:
                match = True
                for key, value in filters.items():
                    # Handle nested keys
                    keys = key.split(".")
                    obj = event
                    for k in keys:
                        if isinstance(obj, dict) and k in obj:
                            obj = obj[k]
                        else:
                            obj = None
                            break
                    
                    # Compare value
                    if obj != value:
                        match = False
                        break
                
                if not match:
                    continue
                    
            filtered_events.append(event)
        
        # Apply pagination
        paginated_events = filtered_events[offset:offset+limit]
        
        # Convert back to AuditEvent objects (not implemented here)
        # In a real implementation, we would convert the dicts back to AuditEvent objects
        # This would require registering event classes or using a factory pattern
        
        return []  # Placeholder - would return the actual events
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        # Nothing to do for file storage
        pass


class APIAuditStorage(AuditStorage):
    """API-based storage backend for audit events.
    
    This class implements storage of audit events via HTTP API calls,
    supporting connection pooling and batch processing.
    
    Attributes:
        config: Audit configuration
        base_url: Base URL for the audit API
        api_key: API key for authentication
        session: HTTP session for connection pooling
        batch_size: Maximum batch size for event submission
        logger: Structured logger
    """
    
    def __init__(
        self,
        config: AuditConfig,
        base_url: str,
        api_key: Optional[str] = None,
        batch_size: int = 50,
        connection_timeout: float = 10.0,
        max_connections: int = 10,
    ) -> None:
        """Initialize API-based audit storage.
        
        Args:
            config: Audit configuration
            base_url: Base URL for the audit API
            api_key: API key for authentication
            batch_size: Maximum batch size for event submission
            connection_timeout: Timeout for API connections in seconds
            max_connections: Maximum number of connections in the pool
        """
        self.config = config
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.batch_size = batch_size
        self.connection_timeout = connection_timeout
        self.max_connections = max_connections
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = structlog.get_logger(__name__)
    
    async def initialize(self) -> None:
        """Initialize the API storage backend."""
        # Create HTTP session for connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            ssl=False,  # Set to True in production
        )
        
        timeout = aiohttp.ClientTimeout(total=self.connection_timeout)
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
        )
    
    async def store_event(self, event: AuditEvent) -> None:
        """Store a single audit event via API.
        
        Args:
            event: Audit event to store
        """
        if not self.session:
            await self.initialize()
            
        # Convert event to dict for API submission
        event_dict = event.to_dict()
        
        # Submit to API
        try:
            assert self.session is not None  # For type checking
            async with self.session.post(
                f"{self.base_url}/events",
                json=event_dict,
            ) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    self.logger.error(
                        "Failed to store audit event via API",
                        status=response.status,
                        response=response_text,
                        event_id=event.id,
                    )
        except Exception as e:
            self.logger.error(
                "Error storing audit event via API",
                error=str(e),
                event_id=event.id,
            )
    
    async def store_events(self, events: List[AuditEvent]) -> None:
        """Store multiple audit events in batch via API.
        
        Args:
            events: List of audit events to store
        """
        if not events:
            return
            
        if not self.session:
            await self.initialize()
            
        # Convert events to dicts for API submission
        event_dicts = [event.to_dict() for event in events]
        
        # Submit events in batches
        for i in range(0, len(event_dicts), self.batch_size):
            batch = event_dicts[i:i+self.batch_size]
            
            # Submit batch to API
            try:
                assert self.session is not None  # For type checking
                async with self.session.post(
                    f"{self.base_url}/events/batch",
                    json={"events": batch},
                ) as response:
                    if response.status >= 400:
                        response_text = await response.text()
                        self.logger.error(
                            "Failed to store audit events batch via API",
                            status=response.status,
                            response=response_text,
                            batch_size=len(batch),
                        )
            except Exception as e:
                self.logger.error(
                    "Error storing audit events batch via API",
                    error=str(e),
                    batch_size=len(batch),
                )
    
    async def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Retrieve audit events based on criteria via API.
        
        Args:
            start_time: Optional start time for filtering events
            end_time: Optional end time for filtering events
            filters: Optional additional filters
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of matching audit events
        """
        if not self.session:
            await self.initialize()
            
        # Build query parameters
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        
        if start_time:
            params["start_time"] = start_time.isoformat()
            
        if end_time:
            params["end_time"] = end_time.isoformat()
            
        if filters:
            for key, value in filters.items():
                params[key] = value
        
        # Fetch events from API
        try:
            assert self.session is not None  # For type checking
            async with self.session.get(
                f"{self.base_url}/events",
                params=params,
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # In a real implementation, we would convert the dicts to AuditEvent objects
                    # This would require registering event classes or using a factory pattern
                    
                    return []  # Placeholder - would return the actual events
                else:
                    response_text = await response.text()
                    self.logger.error(
                        "Failed to retrieve audit events via API",
                        status=response.status,
                        response=response_text,
                    )
                    return []
        except Exception as e:
            self.logger.error(
                "Error retrieving audit events via API",
                error=str(e),
            )
            return []
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None


class DatabaseAuditStorage(AuditStorage):
    """Database-based storage backend for audit events.
    
    This is a placeholder implementation. In a real implementation,
    this would use an async database client to store events in a database.
    
    Attributes:
        config: Audit configuration
    """
    
    def __init__(self, config: AuditConfig, **db_config: Any) -> None:
        """Initialize database-based audit storage.
        
        Args:
            config: Audit configuration
            **db_config: Database-specific configuration
        """
        self.config = config
        self.db_config = db_config
    
    async def initialize(self) -> None:
        """Initialize the database storage backend."""
        # In a real implementation, this would connect to the database
        pass
    
    async def store_event(self, event: AuditEvent) -> None:
        """Store a single audit event in the database.
        
        Args:
            event: Audit event to store
        """
        # In a real implementation, this would store the event in the database
        pass
    
    async def store_events(self, events: List[AuditEvent]) -> None:
        """Store multiple audit events in batch in the database.
        
        Args:
            events: List of audit events to store
        """
        # In a real implementation, this would store the events in the database
        pass
    
    async def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Retrieve audit events based on criteria from the database.
        
        Args:
            start_time: Optional start time for filtering events
            end_time: Optional end time for filtering events
            filters: Optional additional filters
            limit: Maximum number of events to return
            offset: Offset for pagination
            
        Returns:
            List of matching audit events
        """
        # In a real implementation, this would query the database
        return []
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        # In a real implementation, this would close the database connection
        pass


class AuditClient:
    """Audit client for the DeepSentinel SDK.
    
    This class handles audit event logging, storage, batch processing,
    and performance metrics collection.
    
    Attributes:
        config: Audit configuration
        storage: Audit storage backend
        batch_size: Maximum batch size for event submission
        batch_interval_sec: Interval for batch processing in seconds
        pending_events: List of pending audit events
        logger: Structured logger
    """
    
    # Map of storage backend types to their classes
    STORAGE_BACKENDS: Dict[str, Type[AuditStorage]] = {
        "file": FileAuditStorage,
        "api": APIAuditStorage,
        "database": DatabaseAuditStorage,
    }
    
    def __init__(
        self,
        config: AuditConfig,
        storage_backend: Optional[AuditStorage] = None,
        batch_size: int = 100,
        batch_interval_sec: float = 5.0,
        metrics_collector: Optional[MetricsCollector] = None,
    ) -> None:
        """Initialize the audit client.
        
        Args:
            config: Audit configuration
            storage_backend: Custom storage backend (if not specified, one will be
                created based on the configuration)
            batch_size: Maximum batch size for event submission
            batch_interval_sec: Interval for batch processing in seconds
            metrics_collector: Optional metrics collector for performance tracking
        """
        self.config = config
        self.storage = storage_backend
        self.batch_size = batch_size
        self.batch_interval_sec = batch_interval_sec
        self.pending_events: List[AuditEvent] = []
        self.logger = structlog.get_logger(__name__)
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Batch processing task
        self._batch_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self._start_time = time.time()
        self._event_count = 0
        self._error_count = 0
        
        # Comprehensive metrics collector
        self._metrics_collector = metrics_collector or MetricsCollector(
            enabled=True,
            window_size=1000,
            retention_minutes=60,
        )
        
        # Track events that have been seen
        self._seen_events: Set[str] = set()
    
    async def initialize(self) -> None:
        """Initialize the audit client.
        
        This sets up the storage backend and starts the batch processing task.
        """
        # Create storage backend if not provided
        if not self.storage:
            await self._create_storage_backend()
            
        # Initialize storage backend
        if self.storage:
            await self.storage.initialize()
            
        # Start batch processing task
        if self.config.enabled and self.batch_interval_sec > 0:
            self._batch_task = asyncio.create_task(self._process_batches())
    
    async def _create_storage_backend(self) -> None:
        """Create a storage backend based on the configuration."""
        backend_type = self.config.storage_backend.lower()
        
        if backend_type in self.STORAGE_BACKENDS:
            backend_class = self.STORAGE_BACKENDS[backend_type]
            
            # Get backend-specific configuration
            backend_config = self.config.storage_config or {}
            
            # Create backend instance
            if backend_type == "file":
                self.storage = backend_class(self.config, **backend_config)
            elif backend_type == "api":
                # Ensure required configuration is provided
                if "base_url" not in backend_config:
                    self.logger.error(
                        "Missing required configuration for API storage backend",
                        missing="base_url",
                    )
                    return
                    
                self.storage = backend_class(self.config, **backend_config)
            elif backend_type == "database":
                self.storage = backend_class(self.config, **backend_config)
        else:
            self.logger.error(
                "Unsupported storage backend",
                backend_type=backend_type,
            )
    
    async def log_event(self, event: AuditEvent) -> None:
        """Log an audit event.
        
        If batch processing is enabled, the event will be added to the batch.
        Otherwise, it will be stored immediately.
        
        Args:
            event: Audit event to log
        """
        if not self.config.enabled:
            return
            
        # Check if we've seen this event before
        if event.id in self._seen_events:
            return
            
        self._seen_events.add(event.id)
        
        # Track metrics
        self._event_count += 1
        start_time = time.time()
        
        # If no storage backend or batch processing is disabled, do nothing
        if not self.storage:
            return
            
        try:
            if self.batch_interval_sec > 0:
                # Add to batch
                async with self._lock:
                    self.pending_events.append(event)
                    
                    # If batch is full, process it immediately
                    if len(self.pending_events) >= self.batch_size:
                        await self._flush_batch()
            else:
                # Store immediately
                await self.storage.store_event(event)
            
            # Record successful audit operation
            duration = time.time() - start_time
            self._metrics_collector.record_request(
                provider="audit_system",
                operation="log_event",
                duration=duration,
                success=True,
            )
            
        except Exception as e:
            self._error_count += 1
            duration = time.time() - start_time
            
            # Record failed audit operation
            self._metrics_collector.record_request(
                provider="audit_system",
                operation="log_event",
                duration=duration,
                success=False,
                error=str(e),
            )
            
            self.logger.error(
                "Error logging audit event",
                error=str(e),
                event_id=event.id,
            )
    
    async def log_events(self, events: List[AuditEvent]) -> None:
        """Log multiple audit events.
        
        Args:
            events: List of audit events to log
        """
        if not self.config.enabled or not events:
            return
            
        # Filter out events we've seen before
        new_events = []
        for event in events:
            if event.id not in self._seen_events:
                self._seen_events.add(event.id)
                new_events.append(event)
                
        if not new_events:
            return
            
        # Track metrics
        self._event_count += len(new_events)
        
        # If no storage backend or batch processing is disabled, do nothing
        if not self.storage:
            return
            
        try:
            if self.batch_interval_sec > 0:
                # Add to batch
                async with self._lock:
                    self.pending_events.extend(new_events)
                    
                    # If batch is full, process it immediately
                    if len(self.pending_events) >= self.batch_size:
                        await self._flush_batch()
            else:
                # Store immediately
                await self.storage.store_events(new_events)
        except Exception as e:
            self._error_count += len(new_events)
            self.logger.error(
                "Error logging audit events batch",
                error=str(e),
                event_count=len(new_events),
            )
    
    async def _process_batches(self) -> None:
        """Process batches of audit events periodically."""
        try:
            while True:
                # Wait for the batch interval
                await asyncio.sleep(self.batch_interval_sec)
                
                # Process batch
                await self._flush_batch()
        except asyncio.CancelledError:
            # Task was cancelled, flush final batch
            await self._flush_batch()
        except Exception as e:
            self.logger.error("Error in batch processing task", error=str(e))
    
    async def _flush_batch(self) -> None:
        """Flush the current batch of audit events to storage."""
        if not self.storage or not self.pending_events:
            return
            
        try:
            # Get current batch
            async with self._lock:
                events = self.pending_events.copy()
                self.pending_events.clear()
                
            if events:
                # Store batch
                await self.storage.store_events(events)
        except Exception as e:
            self._error_count += len(events)
            self.logger.error(
                "Error flushing audit events batch",
                error=str(e),
                event_count=len(events),
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the audit client.
        
        Returns:
            Performance metrics including comprehensive stats
        """
        elapsed_time = time.time() - self._start_time
        events_per_sec = 0
        error_rate = 0
        
        if elapsed_time > 0:
            events_per_sec = self._event_count / elapsed_time
            
        if self._event_count > 0:
            error_rate = self._error_count / self._event_count
        
        # Get comprehensive metrics from the collector
        comprehensive_metrics = self._metrics_collector.get_overall_metrics()
        
        return {
            "basic_metrics": {
                "total_duration_ms": elapsed_time * 1000,
                "events_per_second": events_per_sec,
                "events_per_minute": events_per_sec * 60,
                "total_events": self._event_count,
                "error_count": self._error_count,
                "error_rate": error_rate,
                "pending_events": len(self.pending_events),
            },
            "comprehensive_metrics": comprehensive_metrics,
            "audit_specific": {
                "seen_events_count": len(self._seen_events),
                "batch_size": self.batch_size,
                "batch_interval_sec": self.batch_interval_sec,
                "storage_backend": type(self.storage).__name__ if self.storage else None,
            },
        }
    
    async def get_metrics_report(self) -> Dict[str, Any]:
        """Get a comprehensive metrics report including trends.
        
        Returns:
            Comprehensive metrics report
        """
        return self._metrics_collector.generate_report()
    
    async def log_audit_entry(self, entry: AuditEntry) -> None:
        """Log an audit entry.
        
        This converts the entry to an appropriate audit event and logs it.
        
        Args:
            entry: Audit entry to log
        """
        # Convert to an audit event based on the operation type
        from .events import AuditEventType
        
        event_type = AuditEventType.CUSTOM
        if entry.operation.startswith("chat"):
            event_type = AuditEventType.CHAT_RESPONSE
        elif entry.operation.startswith("completion"):
            event_type = AuditEventType.COMPLETION_RESPONSE
        elif entry.operation.startswith("embedding"):
            event_type = AuditEventType.EMBEDDING_RESPONSE
            
        # Create a basic audit event
        event = AuditEvent(
            id=entry.id,
            event_type=event_type,
            timestamp=entry.timestamp,
            user_id=entry.user_id,
            session_id=entry.session_id,
            source="middleware",
            details={
                "provider": entry.provider,
                "model": entry.model,
                "request_data": entry.request_data,
                "response_data": entry.response_data,
                "compliance_checks": [check.model_dump() for check in entry.compliance_checks],
                "cost": entry.cost,
                "metrics": {
                    "total_duration_ms": entry.duration_ms,
                },
            },
            metadata=entry.metadata,
        )
        
        # Log the event
        await self.log_event(event)
    
    async def cleanup(self) -> None:
        """Clean up resources used by the audit client.
        
        This stops the batch processing task and cleans up the storage backend.
        """
        # Cancel batch processing task
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None
            
        # Flush any remaining events
        await self._flush_batch()
        
        # Clean up storage backend
        if self.storage:
            await self.storage.cleanup()
        
        # Clean up metrics collector
        if self._metrics_collector:
            await self._metrics_collector.close()
    
    async def __aenter__(self) -> "AuditClient":
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Async context manager exit."""
        await self.cleanup()