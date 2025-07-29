"""Main detection engine for sensitive data pattern matching.

This module provides the core detection engine that coordinates multiple
detection modules to identify sensitive data patterns in text content.
"""

import asyncio
from typing import Any, Dict, List, Optional

import structlog

from ...config import SentinelConfig
from .patterns import PatternMatcher
from .pii import PIIDetector
from .phi import PHIDetector
from .pci import PCIDetector


class DetectionEngine:
    """Main detection engine for sensitive data identification.
    
    This class coordinates multiple detection modules to identify various
    types of sensitive data patterns in text content.
    
    Attributes:
        config: Sentinel configuration
        engines: Dictionary of detection engines by name
        logger: Structured logger
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the detection engine.
        
        Args:
            config: Sentinel configuration
        """
        self.config = config
        self.logger = structlog.get_logger(__name__)
        
        # Initialize detection engines
        self.engines: Dict[str, Any] = {}
        self._initialize_engines()
        
        # Performance metrics
        self._total_analyses = 0
        self._total_matches = 0
        
        self.logger.info(
            "Detection engine initialized",
            engine_count=len(self.engines),
        )
    
    def _initialize_engines(self) -> None:
        """Initialize all detection engines."""
        try:
            # Pattern matcher for custom patterns
            self.engines["pattern_matcher"] = PatternMatcher(self.config)
            
            # PII detector
            self.engines["pii_detector"] = PIIDetector(self.config)
            
            # PHI detector
            self.engines["phi_detector"] = PHIDetector(self.config)
            
            # PCI detector
            self.engines["pci_detector"] = PCIDetector(self.config)
            
            self.logger.info(
                "Detection engines initialized",
                engines=list(self.engines.keys()),
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to initialize detection engines",
                error=str(e),
            )
            raise
    
    async def analyze_text(
        self,
        text_content: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze text content for sensitive data patterns.
        
        Args:
            text_content: List of text strings to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing detection results from all engines
        """
        if not text_content:
            return {}
        
        context = context or {}
        self._total_analyses += 1
        
        # Combine all text content for analysis
        combined_text = "\n".join(text_content)
        
        # Run all detection engines concurrently
        detection_tasks = []
        for engine_name, engine in self.engines.items():
            task = asyncio.create_task(
                self._run_engine_analysis(
                    engine_name, engine, combined_text, context
                )
            )
            detection_tasks.append(task)
        
        # Wait for all analyses to complete
        results = await asyncio.gather(
            *detection_tasks, return_exceptions=True
        )
        
        # Combine results
        combined_results = {}
        for i, (engine_name, result) in enumerate(
            zip(self.engines.keys(), results)
        ):
            if isinstance(result, Exception):
                self.logger.error(
                    "Detection engine failed",
                    engine=engine_name,
                    error=str(result),
                )
                combined_results[engine_name] = {
                    "error": str(result),
                    "matches": [],
                }
            else:
                combined_results[engine_name] = result
                # Count matches for metrics
                if "matches" in result:
                    self._total_matches += len(result["matches"])
        
        return combined_results
    
    async def _run_engine_analysis(
        self,
        engine_name: str,
        engine: Any,
        text: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run analysis for a specific detection engine.
        
        Args:
            engine_name: Name of the detection engine
            engine: Detection engine instance
            text: Text to analyze
            context: Context information
            
        Returns:
            Detection results from the engine
        """
        try:
            if hasattr(engine, "analyze_async"):
                return await engine.analyze_async(text, context)
            elif hasattr(engine, "analyze"):
                # Run synchronous analysis in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, engine.analyze, text, context
                )
            else:
                raise AttributeError(
                    f"Engine {engine_name} has no analyze method"
                )
        except Exception as e:
            self.logger.error(
                "Engine analysis failed",
                engine=engine_name,
                error=str(e),
            )
            raise
    
    async def analyze_single_text(
        self,
        text: str,
        engine_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze a single text string with specified engines.
        
        Args:
            text: Text string to analyze
            engine_names: Optional list of engine names to use
            context: Optional context information
            
        Returns:
            Dictionary containing detection results
        """
        if not text.strip():
            return {}
        
        context = context or {}
        engines_to_use = engine_names or list(self.engines.keys())
        
        # Filter engines that exist
        valid_engines = {
            name: engine for name, engine in self.engines.items()
            if name in engines_to_use
        }
        
        if not valid_engines:
            return {}
        
        # Run selected engines
        detection_tasks = []
        for engine_name, engine in valid_engines.items():
            task = asyncio.create_task(
                self._run_engine_analysis(engine_name, engine, text, context)
            )
            detection_tasks.append(task)
        
        # Wait for analyses to complete
        results = await asyncio.gather(
            *detection_tasks, return_exceptions=True
        )
        
        # Combine results
        combined_results = {}
        for engine_name, result in zip(valid_engines.keys(), results):
            if isinstance(result, Exception):
                self.logger.error(
                    "Detection engine failed",
                    engine=engine_name,
                    error=str(result),
                )
                combined_results[engine_name] = {
                    "error": str(result),
                    "matches": [],
                }
            else:
                combined_results[engine_name] = result
        
        return combined_results
    
    def get_engine(self, engine_name: str) -> Optional[Any]:
        """Get a specific detection engine by name.
        
        Args:
            engine_name: Name of the detection engine
            
        Returns:
            Detection engine instance or None if not found
        """
        return self.engines.get(engine_name)
    
    def list_engines(self) -> List[str]:
        """Get list of available detection engine names.
        
        Returns:
            List of detection engine names
        """
        return list(self.engines.keys())
    
    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific detection engine.
        
        Args:
            engine_name: Name of the detection engine
            
        Returns:
            Dictionary containing engine information
        """
        engine = self.engines.get(engine_name)
        if not engine:
            return None
        
        info = {
            "name": engine_name,
            "type": type(engine).__name__,
            "enabled": getattr(engine, "enabled", True),
        }
        
        # Add engine-specific information
        if hasattr(engine, "get_info"):
            info.update(engine.get_info())
        
        return info
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detection engine performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        return {
            "total_analyses": self._total_analyses,
            "total_matches": self._total_matches,
            "average_matches_per_analysis": (
                self._total_matches / max(self._total_analyses, 1)
            ),
            "engine_count": len(self.engines),
            "engines": list(self.engines.keys()),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all detection engines.
        
        Returns:
            Health check results
        """
        try:
            engine_health = {}
            
            for engine_name, engine in self.engines.items():
                try:
                    if hasattr(engine, "health_check"):
                        if hasattr(engine, "health_check_async"):
                            health = await engine.health_check_async()
                        else:
                            health = engine.health_check()
                    else:
                        # Basic health check - try to analyze empty text
                        await self._run_engine_analysis(
                            engine_name, engine, "", {}
                        )
                        health = {"status": "healthy"}
                    
                    engine_health[engine_name] = health
                    
                except Exception as e:
                    engine_health[engine_name] = {
                        "status": "error",
                        "error": str(e),
                    }
            
            # Determine overall status
            failed_engines = [
                name for name, health in engine_health.items()
                if health.get("status") == "error"
            ]
            
            overall_status = "healthy"
            if failed_engines:
                if len(failed_engines) == len(self.engines):
                    overall_status = "error"
                else:
                    overall_status = "degraded"
            
            return {
                "status": overall_status,
                "engines": engine_health,
                "failed_engines": failed_engines,
                "metrics": self.get_metrics(),
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def reload_engines(self) -> None:
        """Reload all detection engines with updated configuration."""
        try:
            self.logger.info("Reloading detection engines")
            
            # Clear existing engines
            old_engines = list(self.engines.keys())
            self.engines.clear()
            
            # Reinitialize engines
            self._initialize_engines()
            
            self.logger.info(
                "Detection engines reloaded",
                old_engines=old_engines,
                new_engines=list(self.engines.keys()),
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to reload detection engines",
                error=str(e),
            )
            raise
    
    def enable_engine(self, engine_name: str) -> bool:
        """Enable a specific detection engine.
        
        Args:
            engine_name: Name of the engine to enable
            
        Returns:
            True if engine was enabled, False if not found
        """
        engine = self.engines.get(engine_name)
        if engine and hasattr(engine, "enable"):
            engine.enable()
            self.logger.info("Detection engine enabled", engine=engine_name)
            return True
        return False
    
    def disable_engine(self, engine_name: str) -> bool:
        """Disable a specific detection engine.
        
        Args:
            engine_name: Name of the engine to disable
            
        Returns:
            True if engine was disabled, False if not found
        """
        engine = self.engines.get(engine_name)
        if engine and hasattr(engine, "disable"):
            engine.disable()
            self.logger.info("Detection engine disabled", engine=engine_name)
            return True
        return False