"""PII (Personally Identifiable Information) detection module.

This module provides specialized detection for PII data types including
emails, phone numbers, social security numbers, and other personal identifiers.
"""

import re
from typing import Any, Dict, List, Optional

import structlog

from ...config import SentinelConfig
from .patterns import PatternMatcher


class PIIDetector:
    """Specialized detector for PII data patterns.
    
    This detector focuses on identifying personally identifiable information
    such as emails, phone numbers, SSNs, addresses, and other personal data.
    
    Attributes:
        config: Sentinel configuration
        pattern_matcher: Base pattern matcher
        enabled: Whether the detector is enabled
        sensitivity_level: Detection sensitivity (low, medium, high)
        logger: Structured logger
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the PII detector.
        
        Args:
            config: Sentinel configuration
        """
        self.config = config
        self.enabled = True
        self.sensitivity_level = "medium"
        self.logger = structlog.get_logger(__name__)
        
        # Initialize pattern matcher with PII-specific patterns
        self.pattern_matcher = PatternMatcher(config)
        self._load_pii_patterns()
        
        self.logger.info(
            "PII detector initialized",
            sensitivity=self.sensitivity_level,
            patterns=len(self.pattern_matcher.patterns),
        )
    
    def _load_pii_patterns(self) -> None:
        """Load PII-specific detection patterns."""
        pii_patterns = {
            # Enhanced email patterns
            "email_detailed": {
                "pattern": (
                    r"\b[A-Za-z0-9]([A-Za-z0-9._%-]*[A-Za-z0-9])?"
                    r"@[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}\b"
                ),
                "type": "EMAIL",
                "confidence": 0.95,
                "flags": re.IGNORECASE,
            },
            # International phone patterns
            "phone_international": {
                "pattern": (
                    r"\b(?:\+?[1-9]\d{0,3})?[-.\s]?"
                    r"(?:\(\d{1,4}\)|\d{1,4})[-.\s]?"
                    r"\d{1,4}[-.\s]?\d{1,9}\b"
                ),
                "type": "PHONE",
                "confidence": 0.7,
                "flags": 0,
            },
            # US SSN with validation
            "ssn_formatted": {
                "pattern": (
                    r"\b(?!000|666|9\d{2})(?!00)\d{3}[-\s]?"
                    r"(?!00)\d{2}[-\s]?(?!0000)\d{4}\b"
                ),
                "type": "SSN",
                "confidence": 0.9,
                "flags": 0,
            },
            # Driver's license patterns
            "drivers_license": {
                "pattern": (
                    r"\b(?:DL|DRIVER.?LICENSE|LICENSE)[:\s#]*"
                    r"[A-Z0-9]{8,15}\b"
                ),
                "type": "DRIVERS_LICENSE",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Passport numbers
            "passport": {
                "pattern": (
                    r"\b(?:PASSPORT)[:\s#]*[A-Z0-9]{6,9}\b"
                ),
                "type": "PASSPORT",
                "confidence": 0.85,
                "flags": re.IGNORECASE,
            },
            # Date of birth patterns
            "date_of_birth": {
                "pattern": (
                    r"\b(?:DOB|DATE.?OF.?BIRTH|BIRTH.?DATE)[:\s]*"
                    r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
                    r"\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b"
                ),
                "type": "DATE_OF_BIRTH",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Address patterns (basic)
            "address": {
                "pattern": (
                    r"\b\d{1,5}\s+(?:[A-Za-z0-9]+\s+){1,3}"
                    r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|"
                    r"Drive|Dr|Court|Ct|Place|Pl)\b"
                ),
                "type": "ADDRESS",
                "confidence": 0.7,
                "flags": re.IGNORECASE,
            },
            # Full name patterns
            "full_name": {
                "pattern": (
                    r"\b(?:NAME|FULL.?NAME)[:\s]*"
                    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b"
                ),
                "type": "FULL_NAME",
                "confidence": 0.6,
                "flags": re.IGNORECASE,
            },
            # Government ID patterns
            "government_id": {
                "pattern": (
                    r"\b(?:ID|GOVERNMENT.?ID|FEDERAL.?ID)[:\s#]*"
                    r"[A-Z0-9]{8,12}\b"
                ),
                "type": "GOVERNMENT_ID",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
        }
        
        # Add patterns to matcher
        for name, pattern_info in pii_patterns.items():
            self.pattern_matcher.add_pattern(
                name=name,
                pattern=pattern_info["pattern"],
                pattern_type=pattern_info["type"],
                confidence=pattern_info["confidence"],
                flags=pattern_info.get("flags", 0),
            )
    
    def analyze(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for PII patterns.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing PII detection results
        """
        if not self.enabled or not text.strip():
            return {"matches": [], "pii_types": [], "risk_level": "none"}
        
        context = context or {}
        
        # Run base pattern matching
        pattern_results = self.pattern_matcher.analyze(text, context)
        matches = []
        
        # Convert pattern matches to PII matches with additional processing
        for match_dict in pattern_results.get("matches", []):
            pii_match = self._process_pii_match(match_dict, text)
            if pii_match:
                matches.append(pii_match)
        
        # Apply sensitivity filtering
        filtered_matches = self._apply_sensitivity_filter(matches)
        
        # Calculate risk assessment
        risk_assessment = self._calculate_risk_level(filtered_matches)
        
        # Get unique PII types found
        pii_types = list(set(match["type"] for match in filtered_matches))
        
        return {
            "matches": filtered_matches,
            "pii_types": pii_types,
            "total_matches": len(filtered_matches),
            "risk_level": risk_assessment["level"],
            "risk_score": risk_assessment["score"],
            "high_confidence_matches": len([
                m for m in filtered_matches if m["confidence"] >= 0.8
            ]),
        }
    
    async def analyze_async(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Async wrapper for analyze method.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing PII detection results
        """
        return self.analyze(text, context)
    
    def _process_pii_match(
        self, match_dict: Dict[str, Any], full_text: str
    ) -> Optional[Dict[str, Any]]:
        """Process and validate a PII match.
        
        Args:
            match_dict: Raw pattern match dictionary
            full_text: Full text being analyzed
            
        Returns:
            Processed PII match or None if invalid
        """
        # Additional validation based on PII type
        pii_type = match_dict["type"]
        match_text = match_dict["text"]
        
        # Context-based confidence adjustment
        adjusted_confidence = self._adjust_confidence_by_context(
            match_dict, full_text
        )
        
        # Apply PII-specific validation
        if not self._validate_pii_match(match_text, pii_type):
            return None
        
        return {
            "text": match_text,
            "type": pii_type,
            "start": match_dict["start"],
            "end": match_dict["end"],
            "confidence": adjusted_confidence,
            "pattern_name": match_dict["pattern_name"],
            "metadata": {
                **match_dict.get("metadata", {}),
                "validation_passed": True,
                "original_confidence": match_dict["confidence"],
            },
        }
    
    def _adjust_confidence_by_context(
        self, match_dict: Dict[str, Any], full_text: str
    ) -> float:
        """Adjust confidence based on surrounding context.
        
        Args:
            match_dict: Pattern match dictionary
            full_text: Full text being analyzed
            
        Returns:
            Adjusted confidence score
        """
        base_confidence = match_dict["confidence"]
        pii_type = match_dict["type"]
        start_pos = match_dict["start"]
        end_pos = match_dict["end"]
        
        # Get surrounding context (50 characters before and after)
        context_start = max(0, start_pos - 50)
        context_end = min(len(full_text), end_pos + 50)
        context = full_text[context_start:context_end].lower()
        
        # Context keywords that increase confidence
        positive_contexts = {
            "EMAIL": ["email", "e-mail", "contact", "send", "reply"],
            "PHONE": ["phone", "call", "number", "contact", "mobile"],
            "SSN": ["ssn", "social", "security", "tax", "benefits"],
            "ADDRESS": ["address", "street", "home", "mail", "ship"],
            "FULL_NAME": ["name", "patient", "customer", "employee"],
        }
        
        # Context keywords that decrease confidence
        negative_contexts = {
            "EMAIL": ["example", "test", "sample", "dummy"],
            "PHONE": ["example", "xxx", "000"],
            "SSN": ["example", "xxx", "000"],
        }
        
        confidence_adjustment = 0.0
        
        # Check positive contexts
        if pii_type in positive_contexts:
            for keyword in positive_contexts[pii_type]:
                if keyword in context:
                    confidence_adjustment += 0.1
                    break
        
        # Check negative contexts
        if pii_type in negative_contexts:
            for keyword in negative_contexts[pii_type]:
                if keyword in context:
                    confidence_adjustment -= 0.2
                    break
        
        # Apply adjustment
        adjusted_confidence = min(
            1.0, max(0.0, base_confidence + confidence_adjustment)
        )
        
        return adjusted_confidence
    
    def _validate_pii_match(self, match_text: str, pii_type: str) -> bool:
        """Validate PII match using type-specific rules.
        
        Args:
            match_text: Matched text
            pii_type: Type of PII
            
        Returns:
            True if valid, False otherwise
        """
        # Email validation
        if pii_type == "EMAIL":
            return self._validate_email(match_text)
        
        # Phone validation
        elif pii_type == "PHONE":
            return self._validate_phone(match_text)
        
        # SSN validation
        elif pii_type == "SSN":
            return self._validate_ssn_advanced(match_text)
        
        # Default validation
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Advanced email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check for common test/example domains
        test_domains = [
            "example.com", "test.com", "sample.com", "dummy.com",
            "localhost", "invalid", "example.org", "example.net"
        ]
        
        domain = email.split("@")[-1].lower()
        if domain in test_domains:
            return False
        
        # Check for obvious fake patterns
        if "test" in email.lower() or "example" in email.lower():
            return False
        
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """Advanced phone number validation.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Check for invalid patterns
        if len(digits) < 7 or len(digits) > 15:
            return False
        
        # Check for repeated digits (likely fake)
        if len(set(digits)) <= 2:
            return False
        
        # Check for common fake patterns
        fake_patterns = ["1234567", "0000000", "1111111"]
        if any(pattern in digits for pattern in fake_patterns):
            return False
        
        return True
    
    def _validate_ssn_advanced(self, ssn: str) -> bool:
        """Advanced SSN validation.
        
        Args:
            ssn: SSN to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Use base SSN validation from pattern matcher
        return self.pattern_matcher._validate_ssn(ssn)
    
    def _apply_sensitivity_filter(
        self, matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter matches based on sensitivity level.
        
        Args:
            matches: List of PII matches
            
        Returns:
            Filtered list of matches
        """
        if self.sensitivity_level == "low":
            # Only high-confidence matches
            return [m for m in matches if m["confidence"] >= 0.9]
        elif self.sensitivity_level == "medium":
            # Medium and high-confidence matches
            return [m for m in matches if m["confidence"] >= 0.7]
        else:  # high sensitivity
            # All matches above minimum threshold
            return [m for m in matches if m["confidence"] >= 0.5]
    
    def _calculate_risk_level(
        self, matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall risk level based on PII matches.
        
        Args:
            matches: List of PII matches
            
        Returns:
            Risk assessment dictionary
        """
        if not matches:
            return {"level": "none", "score": 0.0}
        
        # Risk scoring based on PII types and confidence
        risk_weights = {
            "SSN": 1.0,
            "DRIVERS_LICENSE": 0.9,
            "PASSPORT": 0.9,
            "GOVERNMENT_ID": 0.8,
            "EMAIL": 0.6,
            "PHONE": 0.6,
            "FULL_NAME": 0.5,
            "ADDRESS": 0.7,
            "DATE_OF_BIRTH": 0.8,
        }
        
        total_risk = 0.0
        for match in matches:
            pii_type = match["type"]
            confidence = match["confidence"]
            weight = risk_weights.get(pii_type, 0.5)
            total_risk += weight * confidence
        
        # Normalize risk score
        max_possible_risk = len(matches) * 1.0
        normalized_risk = min(1.0, total_risk / max(max_possible_risk, 1.0))
        
        # Determine risk level
        if normalized_risk >= 0.8:
            level = "critical"
        elif normalized_risk >= 0.6:
            level = "high"
        elif normalized_risk >= 0.3:
            level = "medium"
        elif normalized_risk > 0:
            level = "low"
        else:
            level = "none"
        
        return {
            "level": level,
            "score": normalized_risk,
            "total_risk": total_risk,
            "match_count": len(matches),
        }
    
    def set_sensitivity_level(self, level: str) -> None:
        """Set the detection sensitivity level.
        
        Args:
            level: Sensitivity level ("low", "medium", "high")
        """
        if level in ["low", "medium", "high"]:
            self.sensitivity_level = level
            self.logger.info("Sensitivity level updated", level=level)
        else:
            raise ValueError(
                "Invalid sensitivity level. Use: low, medium, high"
            )
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the PII detector.
        
        Returns:
            Dictionary containing detector information
        """
        return {
            "enabled": self.enabled,
            "sensitivity_level": self.sensitivity_level,
            "pattern_count": len(self.pattern_matcher.patterns),
            "supported_types": [
                "EMAIL", "PHONE", "SSN", "DRIVERS_LICENSE", "PASSPORT",
                "DATE_OF_BIRTH", "ADDRESS", "FULL_NAME", "GOVERNMENT_ID"
            ],
        }
    
    def enable(self) -> None:
        """Enable the PII detector."""
        self.enabled = True
        self.pattern_matcher.enable()
        self.logger.info("PII detector enabled")
    
    def disable(self) -> None:
        """Disable the PII detector."""
        self.enabled = False
        self.pattern_matcher.disable()
        self.logger.info("PII detector disabled")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the PII detector.
        
        Returns:
            Health check results
        """
        try:
            # Test with sample PII data
            test_text = "Contact: john.doe@email.com, phone: 555-123-4567"
            result = self.analyze(test_text)
            
            return {
                "status": "healthy",
                "enabled": self.enabled,
                "sensitivity": self.sensitivity_level,
                "test_matches": result["total_matches"],
                "pattern_matcher_status": (
                    self.pattern_matcher.health_check()["status"]
                ),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }