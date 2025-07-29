"""Pattern matching utilities for sensitive data detection.

This module provides base pattern matching functionality that can be used
by various detection engines to identify sensitive data patterns.
"""

import re
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional

import structlog

from ...config import SentinelConfig


class PatternMatch:
    """Represents a pattern match result.
    
    Attributes:
        text: The matched text
        start: Start position in the original text
        end: End position in the original text
        pattern_name: Name of the pattern that matched
        pattern_type: Type/category of the pattern
        confidence: Confidence score (0.0 to 1.0)
        metadata: Additional metadata about the match
    """
    
    def __init__(
        self,
        text: str,
        start: int,
        end: int,
        pattern_name: str,
        pattern_type: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a pattern match.
        
        Args:
            text: The matched text
            start: Start position in the original text
            end: End position in the original text
            pattern_name: Name of the pattern that matched
            pattern_type: Type/category of the pattern
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata about the match
        """
        self.text = text
        self.start = start
        self.end = end
        self.pattern_name = pattern_name
        self.pattern_type = pattern_type
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert match to dictionary.
        
        Returns:
            Dictionary representation of the match
        """
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "pattern_name": self.pattern_name,
            "type": self.pattern_type,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class PatternMatcher:
    """Base pattern matcher for sensitive data detection.
    
    This class provides pattern matching functionality using regex
    and other techniques to identify sensitive data patterns in text.
    
    Attributes:
        config: Sentinel configuration
        patterns: Dictionary of compiled regex patterns
        enabled: Whether the pattern matcher is enabled
        logger: Structured logger
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the pattern matcher.
        
        Args:
            config: Sentinel configuration
        """
        self.config = config
        self.enabled = True
        self.logger = structlog.get_logger(__name__)
        
        # Pattern storage with compiled patterns cache
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self._compiled_patterns_cache: OrderedDict[str, re.Pattern] = (
            OrderedDict()
        )
        self._cache_max_size = 1000
        
        # Performance metrics
        self._performance_stats = {
            "total_matches": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "batch_operations": 0,
            "total_processing_time": 0.0,
        }
        
        # Initialize with default patterns
        self._load_default_patterns()
        
        # Load custom patterns from config
        self._load_custom_patterns()
        
        self.logger.info(
            "Pattern matcher initialized",
            pattern_count=len(self.patterns),
            cache_size=self._cache_max_size,
        )
    
    def _load_default_patterns(self) -> None:
        """Load default regex patterns for common sensitive data."""
        default_patterns = {
            # Email patterns
            "email_basic": {
                "pattern": (
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
                ),
                "type": "EMAIL",
                "confidence": 0.9,
                "flags": re.IGNORECASE,
            },
            # Phone number patterns
            "phone_us": {
                "pattern": (
                    r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?"
                    r"([0-9]{3})[-.\s]?([0-9]{4})\b"
                ),
                "type": "PHONE",
                "confidence": 0.8,
                "flags": 0,
            },
            # SSN patterns
            "ssn_us": {
                "pattern": (
                    r"\b(?!000|666|9\d{2})\d{3}[-\s]?"
                    r"(?!00)\d{2}[-\s]?(?!0000)\d{4}\b"
                ),
                "type": "SSN",
                "confidence": 0.9,
                "flags": 0,
            },
            # Credit card patterns (basic)
            "credit_card": {
                "pattern": (
                    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|"
                    r"3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"
                ),
                "type": "CREDIT_CARD",
                "confidence": 0.7,
                "flags": 0,
            },
            # IP Address patterns
            "ip_address": {
                "pattern": (
                    r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
                ),
                "type": "IP_ADDRESS",
                "confidence": 0.8,
                "flags": 0,
            },
            # URL patterns
            "url": {
                "pattern": r"\b(?:https?://|www\.)[^\s<>\"]+[^\s<>\".,)]",
                "type": "URL",
                "confidence": 0.7,
                "flags": re.IGNORECASE,
            },
        }
        
        # Store patterns (compilation happens on-demand)
        for name, pattern_info in default_patterns.items():
            try:
                # Test compilation to validate pattern
                re.compile(
                    pattern_info["pattern"], pattern_info.get("flags", 0)
                )
                
                self.patterns[name] = {
                    "type": pattern_info["type"],
                    "confidence": pattern_info["confidence"],
                    "original": pattern_info["pattern"],
                    "flags": pattern_info.get("flags", 0),
                }
            except re.error as e:
                self.logger.error(
                    "Failed to validate default pattern",
                    pattern_name=name,
                    error=str(e),
                )
    
    def _load_custom_patterns(self) -> None:
        """Load custom patterns from configuration."""
        # Check for custom patterns in compliance policies
        for policy in self.config.compliance_policies:
            if hasattr(policy, "custom_patterns"):
                for i, pattern_str in enumerate(policy.custom_patterns):
                    pattern_name = f"{policy.name}_custom_{i}"
                    try:
                        # Test compilation to validate pattern
                        re.compile(pattern_str, re.IGNORECASE)
                        
                        self.patterns[pattern_name] = {
                            "type": "CUSTOM",
                            "confidence": 0.8,
                            "original": pattern_str,
                            "flags": re.IGNORECASE,
                            "policy": policy.name,
                        }
                    except re.error as e:
                        self.logger.error(
                            "Failed to validate custom pattern",
                            pattern=pattern_str,
                            policy=policy.name,
                            error=str(e),
                        )
    
    def _get_compiled_pattern(
        self, pattern_name: str, pattern_info: Dict[str, Any]
    ) -> re.Pattern:
        """Get compiled pattern with caching for performance.
        
        Args:
            pattern_name: Name of the pattern
            pattern_info: Pattern information dictionary
            
        Returns:
            Compiled regex pattern
        """
        cache_key = f"{pattern_name}:{pattern_info['original']}"
        
        # Check cache first
        if cache_key in self._compiled_patterns_cache:
            # Move to end (LRU)
            self._compiled_patterns_cache.move_to_end(cache_key)
            self._performance_stats["cache_hits"] += 1
            return self._compiled_patterns_cache[cache_key]
        
        # Compile pattern
        try:
            compiled_pattern = re.compile(
                pattern_info["original"],
                pattern_info.get("flags", 0)
            )
            
            # Add to cache
            self._compiled_patterns_cache[cache_key] = compiled_pattern
            self._performance_stats["cache_misses"] += 1
            
            # Evict oldest if cache is full
            if len(self._compiled_patterns_cache) > self._cache_max_size:
                self._compiled_patterns_cache.popitem(last=False)
            
            return compiled_pattern
            
        except re.error as e:
            self.logger.error(
                "Pattern compilation failed",
                pattern=pattern_name,
                error=str(e),
            )
            raise
    
    def analyze(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for pattern matches with performance tracking.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing match results
        """
        start_time = time.time()
        
        if not self.enabled or not text.strip():
            return {
                "matches": [],
                "pattern_count": 0,
                "processing_time": 0.0,
            }
        
        context = context or {}
        matches = []
        
        # Run all patterns against the text
        for pattern_name, pattern_info in self.patterns.items():
            pattern_matches = self._find_pattern_matches(
                text, pattern_name, pattern_info
            )
            matches.extend(pattern_matches)
        
        # Sort matches by position
        matches.sort(key=lambda m: m.start)
        
        # Remove overlapping matches (keep highest confidence)
        matches = self._remove_overlapping_matches(matches)
        
        # Track performance
        processing_time = time.time() - start_time
        self._performance_stats["total_matches"] += len(matches)
        self._performance_stats["total_processing_time"] += processing_time
        
        return {
            "matches": [match.to_dict() for match in matches],
            "pattern_count": len(self.patterns),
            "total_matches": len(matches),
            "match_types": list(set(match.pattern_type for match in matches)),
            "processing_time": processing_time,
        }
    
    async def analyze_batch(
        self, texts: List[str], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze multiple texts in batch for better performance.
        
        Args:
            texts: List of texts to analyze
            context: Optional context information
            
        Returns:
            List of analysis results for each text
        """
        start_time = time.time()
        results = []
        
        for text in texts:
            result = self.analyze(text, context)
            results.append(result)
        
        # Track batch operation
        self._performance_stats["batch_operations"] += 1
        batch_time = time.time() - start_time
        
        self.logger.debug(
            "Batch analysis completed",
            text_count=len(texts),
            total_matches=sum(r["total_matches"] for r in results),
            processing_time=batch_time,
        )
        
        return results
    
    async def analyze_async(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Async wrapper for analyze method.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing match results
        """
        return self.analyze(text, context)
    
    def _find_pattern_matches(
        self, text: str, pattern_name: str, pattern_info: Dict[str, Any]
    ) -> List[PatternMatch]:
        """Find matches for a specific pattern with caching.
        
        Args:
            text: Text to search
            pattern_name: Name of the pattern
            pattern_info: Pattern information dictionary
            
        Returns:
            List of pattern matches
        """
        matches = []
        
        try:
            compiled_pattern = self._get_compiled_pattern(
                pattern_name, pattern_info
            )
            
            for match in compiled_pattern.finditer(text):
                # Additional validation for certain pattern types
                if self._validate_match(
                    match.group(), pattern_info["type"], pattern_info
                ):
                    pattern_match = PatternMatch(
                        text=match.group(),
                        start=match.start(),
                        end=match.end(),
                        pattern_name=pattern_name,
                        pattern_type=pattern_info["type"],
                        confidence=pattern_info["confidence"],
                        metadata={
                            "groups": match.groups(),
                            "groupdict": match.groupdict(),
                        },
                    )
                    matches.append(pattern_match)
        except Exception as e:
            self.logger.error(
                "Pattern matching failed",
                pattern=pattern_name,
                error=str(e),
            )
        
        return matches
    
    def _validate_match(
        self, match_text: str, pattern_type: str, pattern_info: Dict[str, Any]
    ) -> bool:
        """Validate a pattern match using additional checks.
        
        Args:
            match_text: The matched text
            pattern_type: Type of pattern
            pattern_info: Pattern information
            
        Returns:
            True if match is valid, False otherwise
        """
        # Credit card validation using Luhn algorithm
        if pattern_type == "CREDIT_CARD":
            return self._validate_credit_card(match_text)
        
        # SSN validation (basic checks)
        if pattern_type == "SSN":
            return self._validate_ssn(match_text)
        
        # Default validation (always pass)
        return True
    
    def _validate_credit_card(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Credit card number string
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = re.sub(r'\D', '', card_number)
        
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = digits[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit from the right
                n *= 2
                if n > 9:
                    n = n // 10 + n % 10
            total += n
        
        return total % 10 == 0
    
    def _validate_ssn(self, ssn: str) -> bool:
        """Validate SSN format and known invalid patterns.
        
        Args:
            ssn: SSN string
            
        Returns:
            True if valid format, False otherwise
        """
        # Remove non-digits
        digits = re.sub(r'\D', '', ssn)
        
        if len(digits) != 9:
            return False
        
        # Check for invalid patterns
        invalid_patterns = [
            "000000000", "111111111", "222222222", "333333333",
            "444444444", "555555555", "666666666", "777777777",
            "888888888", "999999999", "123456789", "987654321",
        ]
        
        return digits not in invalid_patterns
    
    def _remove_overlapping_matches(
        self, matches: List[PatternMatch]
    ) -> List[PatternMatch]:
        """Remove overlapping matches, keeping highest confidence.
        
        Args:
            matches: List of pattern matches
            
        Returns:
            List of non-overlapping matches
        """
        if not matches:
            return matches
        
        # Sort by position, then by confidence (descending)
        matches.sort(key=lambda m: (m.start, -m.confidence))
        
        non_overlapping = []
        last_end = -1
        
        for match in matches:
            if match.start >= last_end:
                non_overlapping.append(match)
                last_end = match.end
            elif match.confidence > non_overlapping[-1].confidence:
                # Replace previous match if this one has higher confidence
                non_overlapping[-1] = match
                last_end = match.end
        
        return non_overlapping
    
    def add_pattern(
        self,
        name: str,
        pattern: str,
        pattern_type: str,
        confidence: float = 0.8,
        flags: int = 0,
    ) -> bool:
        """Add a new pattern to the matcher.
        
        Args:
            name: Name of the pattern
            pattern: Regular expression pattern
            pattern_type: Type/category of the pattern
            confidence: Confidence score (0.0 to 1.0)
            flags: Regex flags
            
        Returns:
            True if pattern was added successfully, False otherwise
        """
        try:
            # Test compilation to validate pattern
            re.compile(pattern, flags)
            
            self.patterns[name] = {
                "type": pattern_type,
                "confidence": confidence,
                "original": pattern,
                "flags": flags,
            }
            
            # Clear cache entry if it exists
            cache_key = f"{name}:{pattern}"
            if cache_key in self._compiled_patterns_cache:
                del self._compiled_patterns_cache[cache_key]
            
            self.logger.info("Pattern added", name=name, type=pattern_type)
            return True
        except re.error as e:
            self.logger.error(
                "Failed to add pattern",
                name=name,
                pattern=pattern,
                error=str(e),
            )
            return False
    
    def remove_pattern(self, name: str) -> bool:
        """Remove a pattern from the matcher.
        
        Args:
            name: Name of the pattern to remove
            
        Returns:
            True if pattern was removed, False if not found
        """
        if name in self.patterns:
            del self.patterns[name]
            self.logger.info("Pattern removed", name=name)
            return True
        return False
    
    def get_pattern_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific pattern.
        
        Args:
            name: Name of the pattern
            
        Returns:
            Pattern information dictionary or None if not found
        """
        pattern_info = self.patterns.get(name)
        if pattern_info:
            return {
                "name": name,
                "type": pattern_info["type"],
                "confidence": pattern_info["confidence"],
                "pattern": pattern_info["original"],
            }
        return None
    
    def list_patterns(self) -> List[str]:
        """Get list of available pattern names.
        
        Returns:
            List of pattern names
        """
        return list(self.patterns.keys())
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the pattern matcher including performance.
        
        Returns:
            Dictionary containing matcher information and performance stats
        """
        pattern_types = {}
        for pattern_info in self.patterns.values():
            pattern_type = pattern_info["type"]
            pattern_types[pattern_type] = (
                pattern_types.get(pattern_type, 0) + 1
            )
        
        # Calculate cache hit rate
        total_requests = (
            self._performance_stats["cache_hits"] +
            self._performance_stats["cache_misses"]
        )
        cache_hit_rate = (
            self._performance_stats["cache_hits"] / total_requests
            if total_requests > 0 else 0.0
        )
        
        return {
            "enabled": self.enabled,
            "pattern_count": len(self.patterns),
            "pattern_types": pattern_types,
            "cache_size": len(self._compiled_patterns_cache),
            "cache_max_size": self._cache_max_size,
            "performance_stats": {
                **self._performance_stats,
                "cache_hit_rate": cache_hit_rate,
                "avg_processing_time": (
                    self._performance_stats["total_processing_time"] /
                    max(1, self._performance_stats["total_matches"])
                ),
            },
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detailed performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        total_requests = (
            self._performance_stats["cache_hits"] +
            self._performance_stats["cache_misses"]
        )
        
        return {
            "total_matches": self._performance_stats["total_matches"],
            "cache_hits": self._performance_stats["cache_hits"],
            "cache_misses": self._performance_stats["cache_misses"],
            "cache_hit_rate": (
                self._performance_stats["cache_hits"] / total_requests
                if total_requests > 0 else 0.0
            ),
            "batch_operations": self._performance_stats["batch_operations"],
            "total_processing_time": (
                self._performance_stats["total_processing_time"]
            ),
            "avg_processing_time": (
                self._performance_stats["total_processing_time"] /
                max(1, self._performance_stats["total_matches"])
            ),
            "compiled_patterns_cached": len(self._compiled_patterns_cache),
        }
    
    def enable(self) -> None:
        """Enable the pattern matcher."""
        self.enabled = True
        self.logger.info("Pattern matcher enabled")
    
    def disable(self) -> None:
        """Disable the pattern matcher."""
        self.enabled = False
        self.logger.info("Pattern matcher disabled")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the pattern matcher.
        
        Returns:
            Health check results
        """
        try:
            # Test pattern matching with sample text
            test_result = self.analyze("test@example.com 123-45-6789")
            
            return {
                "status": "healthy",
                "enabled": self.enabled,
                "pattern_count": len(self.patterns),
                "test_matches": len(test_result["matches"]),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }