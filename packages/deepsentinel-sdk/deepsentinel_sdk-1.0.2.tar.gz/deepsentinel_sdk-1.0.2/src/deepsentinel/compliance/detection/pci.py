"""PCI (Payment Card Industry) detection module.

This module provides specialized detection for PCI DSS sensitive data types
including credit card numbers, bank account numbers, CVV codes, and other
payment-related information.
"""

import re
from typing import Any, Dict, List, Optional

import structlog

from ...config import SentinelConfig
from .patterns import PatternMatcher


class PCIDetector:
    """Specialized detector for PCI DSS sensitive data patterns.
    
    This detector focuses on identifying payment card industry data
    including credit card numbers, bank accounts, CVV codes, and other
    financial information requiring PCI DSS compliance.
    
    Attributes:
        config: Sentinel configuration
        pattern_matcher: Base pattern matcher
        enabled: Whether the detector is enabled
        strict_validation: Whether to use strict validation
        logger: Structured logger
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the PCI detector.
        
        Args:
            config: Sentinel configuration
        """
        self.config = config
        self.enabled = True
        self.strict_validation = True
        self.logger = structlog.get_logger(__name__)
        
        # Initialize pattern matcher with PCI-specific patterns
        self.pattern_matcher = PatternMatcher(config)
        self._load_pci_patterns()
        
        # Card type mappings
        self.card_types = self._load_card_type_mappings()
        
        self.logger.info(
            "PCI detector initialized",
            patterns=len(self.pattern_matcher.patterns),
            strict_validation=self.strict_validation,
        )
    
    def _load_pci_patterns(self) -> None:
        """Load PCI-specific detection patterns."""
        pci_patterns = {
            # Credit Card Numbers (comprehensive)
            "credit_card_visa": {
                "pattern": r"\b4[0-9]{12}(?:[0-9]{3})?\b",
                "type": "CREDIT_CARD",
                "confidence": 0.9,
                "flags": 0,
                "card_type": "Visa",
            },
            "credit_card_mastercard": {
                "pattern": r"\b5[1-5][0-9]{14}\b",
                "type": "CREDIT_CARD",
                "confidence": 0.9,
                "flags": 0,
                "card_type": "MasterCard",
            },
            "credit_card_amex": {
                "pattern": r"\b3[47][0-9]{13}\b",
                "type": "CREDIT_CARD",
                "confidence": 0.9,
                "flags": 0,
                "card_type": "American Express",
            },
            "credit_card_discover": {
                "pattern": r"\b6(?:011|5[0-9]{2})[0-9]{12}\b",
                "type": "CREDIT_CARD",
                "confidence": 0.9,
                "flags": 0,
                "card_type": "Discover",
            },
            "credit_card_diners": {
                "pattern": r"\b3[0689][0-9]{12}\b",
                "type": "CREDIT_CARD",
                "confidence": 0.8,
                "flags": 0,
                "card_type": "Diners Club",
            },
            "credit_card_jcb": {
                "pattern": r"\b35(?:2[89]|[3-8][0-9])[0-9]{12}\b",
                "type": "CREDIT_CARD",
                "confidence": 0.8,
                "flags": 0,
                "card_type": "JCB",
            },
            # Bank Account Numbers
            "bank_account_us": {
                "pattern": (
                    r"\b(?:ACCOUNT|ACCT)[:\s#]*[0-9]{8,17}\b"
                ),
                "type": "BANK_ACCOUNT",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Routing Numbers (US)
            "routing_number": {
                "pattern": (
                    r"\b(?:ROUTING|RTN)[:\s#]*[0-9]{9}\b"
                ),
                "type": "ROUTING_NUMBER",
                "confidence": 0.9,
                "flags": re.IGNORECASE,
            },
            # CVV/CVC Codes
            "cvv_code": {
                "pattern": (
                    r"\b(?:CVV|CVC|CVV2|CID|CSC)[:\s]*[0-9]{3,4}\b"
                ),
                "type": "CVV",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Expiration Dates
            "card_expiry": {
                "pattern": (
                    r"\b(?:EXP|EXPIRY|EXPIRES?)[:\s]*"
                    r"(?:0[1-9]|1[0-2])[/-](?:[0-9]{2}|20[0-9]{2})\b"
                ),
                "type": "CARD_EXPIRY",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # PIN Numbers
            "pin_number": {
                "pattern": (
                    r"\b(?:PIN)[:\s]*[0-9]{4,6}\b"
                ),
                "type": "PIN",
                "confidence": 0.7,
                "flags": re.IGNORECASE,
            },
            # IBAN (International Bank Account Number)
            "iban": {
                "pattern": (
                    r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}"
                    r"(?:[A-Z0-9]?){0,16}\b"
                ),
                "type": "IBAN",
                "confidence": 0.8,
                "flags": 0,
            },
            # SWIFT/BIC Codes
            "swift_code": {
                "pattern": (
                    r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b"
                ),
                "type": "SWIFT_CODE",
                "confidence": 0.7,
                "flags": 0,
            },
            # Payment Processor Transaction IDs
            "transaction_id": {
                "pattern": (
                    r"\b(?:TXN|TRANSACTION|TRANS)[:\s#]*[A-Z0-9]{10,20}\b"
                ),
                "type": "TRANSACTION_ID",
                "confidence": 0.7,
                "flags": re.IGNORECASE,
            },
        }
        
        # Add patterns to matcher
        for name, pattern_info in pci_patterns.items():
            self.pattern_matcher.add_pattern(
                name=name,
                pattern=pattern_info["pattern"],
                pattern_type=pattern_info["type"],
                confidence=pattern_info["confidence"],
                flags=pattern_info.get("flags", 0),
            )
    
    def _load_card_type_mappings(self) -> Dict[str, str]:
        """Load credit card type identification patterns.
        
        Returns:
            Dictionary mapping patterns to card types
        """
        return {
            r"^4": "Visa",
            r"^5[1-5]": "MasterCard",
            r"^3[47]": "American Express",
            r"^6(?:011|5)": "Discover",
            r"^3[0689]": "Diners Club",
            r"^35(?:2[89]|[3-8])": "JCB",
        }
    
    def analyze(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for PCI-sensitive data patterns.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing PCI detection results
        """
        if not self.enabled or not text.strip():
            return {"matches": [], "pci_types": [], "risk_level": "none"}
        
        context = context or {}
        
        # Run base pattern matching
        pattern_results = self.pattern_matcher.analyze(text, context)
        matches = []
        
        # Process matches with PCI-specific validation
        for match_dict in pattern_results.get("matches", []):
            pci_match = self._process_pci_match(match_dict, text)
            if pci_match:
                matches.append(pci_match)
        
        # Calculate risk assessment
        risk_assessment = self._calculate_pci_risk_level(matches)
        
        # Get unique PCI types found
        pci_types = list(set(match["type"] for match in matches))
        
        return {
            "matches": matches,
            "pci_types": pci_types,
            "total_matches": len(matches),
            "risk_level": risk_assessment["level"],
            "risk_score": risk_assessment["score"],
            "high_risk_matches": len([
                m for m in matches 
                if m["type"] in ["CREDIT_CARD", "BANK_ACCOUNT", "CVV"]
            ]),
            "card_types": self._get_detected_card_types(matches),
        }
    
    async def analyze_async(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Async wrapper for analyze method.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing PCI detection results
        """
        return self.analyze(text, context)
    
    def _process_pci_match(
        self, match_dict: Dict[str, Any], full_text: str
    ) -> Optional[Dict[str, Any]]:
        """Process and validate a PCI match.
        
        Args:
            match_dict: Raw pattern match dictionary
            full_text: Full text being analyzed
            
        Returns:
            Processed PCI match or None if invalid
        """
        pci_type = match_dict["type"]
        match_text = match_dict["text"]
        
        # Apply PCI-specific validation
        if self.strict_validation and not self._validate_pci_match(
            match_text, pci_type
        ):
            return None
        
        # Get additional metadata for credit card matches
        metadata = match_dict.get("metadata", {}).copy()
        if pci_type == "CREDIT_CARD":
            card_info = self._get_card_info(match_text)
            metadata.update(card_info)
        
        return {
            "text": match_text,
            "type": pci_type,
            "start": match_dict["start"],
            "end": match_dict["end"],
            "confidence": match_dict["confidence"],
            "pattern_name": match_dict["pattern_name"],
            "metadata": metadata,
        }
    
    def _validate_pci_match(self, match_text: str, pci_type: str) -> bool:
        """Validate PCI match using type-specific rules.
        
        Args:
            match_text: Matched text
            pci_type: Type of PCI data
            
        Returns:
            True if valid, False otherwise
        """
        # Credit card validation using Luhn algorithm
        if pci_type == "CREDIT_CARD":
            return self._validate_credit_card(match_text)
        
        # Routing number validation
        elif pci_type == "ROUTING_NUMBER":
            return self._validate_routing_number(match_text)
        
        # IBAN validation
        elif pci_type == "IBAN":
            return self._validate_iban(match_text)
        
        # SWIFT code validation
        elif pci_type == "SWIFT_CODE":
            return self._validate_swift_code(match_text)
        
        # Default validation for other types
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
        
        # Check for obvious test numbers
        test_numbers = [
            "4111111111111111",  # Visa test
            "5555555555554444",  # MasterCard test
            "378282246310005",   # Amex test
            "6011111111111117",  # Discover test
        ]
        
        if digits in test_numbers:
            return False
        
        # Luhn algorithm
        return self._luhn_check(digits)
    
    def _validate_routing_number(self, routing_number: str) -> bool:
        """Validate US bank routing number.
        
        Args:
            routing_number: Routing number string
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = re.sub(r'\D', '', routing_number)
        
        if len(digits) != 9:
            return False
        
        # Routing number checksum validation
        weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
        total = sum(int(d) * w for d, w in zip(digits, weights))
        
        return total % 10 == 0
    
    def _validate_iban(self, iban: str) -> bool:
        """Validate International Bank Account Number.
        
        Args:
            iban: IBAN string
            
        Returns:
            True if valid, False otherwise
        """
        # Remove spaces and convert to uppercase
        iban = re.sub(r'\s', '', iban.upper())
        
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Move first 4 characters to end
        rearranged = iban[4:] + iban[:4]
        
        # Replace letters with numbers (A=10, B=11, etc.)
        numeric = ""
        for char in rearranged:
            if char.isalpha():
                numeric += str(ord(char) - ord('A') + 10)
            else:
                numeric += char
        
        # Check if result mod 97 equals 1
        try:
            return int(numeric) % 97 == 1
        except ValueError:
            return False
    
    def _validate_swift_code(self, swift_code: str) -> bool:
        """Validate SWIFT/BIC code format.
        
        Args:
            swift_code: SWIFT code string
            
        Returns:
            True if valid format, False otherwise
        """
        # Remove spaces and convert to uppercase
        swift = re.sub(r'\s', '', swift_code.upper())
        
        # Must be 8 or 11 characters
        if len(swift) not in [8, 11]:
            return False
        
        # First 6 characters must be letters
        if not swift[:6].isalpha():
            return False
        
        # Next 2 characters can be letters or digits
        if not swift[6:8].isalnum():
            return False
        
        # Last 3 characters (if present) can be letters or digits
        if len(swift) == 11 and not swift[8:11].isalnum():
            return False
        
        return True
    
    def _luhn_check(self, digits: str) -> bool:
        """Perform Luhn algorithm check for number validation.
        
        Args:
            digits: String of digits to check
            
        Returns:
            True if passes Luhn check, False otherwise
        """
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
    
    def _get_card_info(self, card_number: str) -> Dict[str, Any]:
        """Get additional information about a credit card.
        
        Args:
            card_number: Credit card number
            
        Returns:
            Dictionary containing card information
        """
        digits = re.sub(r'\D', '', card_number)
        
        # Determine card type
        card_type = "Unknown"
        for pattern, card_name in self.card_types.items():
            if re.match(pattern, digits):
                card_type = card_name
                break
        
        return {
            "card_type": card_type,
            "card_length": len(digits),
            "masked_number": self._mask_card_number(digits),
            "last_four": digits[-4:] if len(digits) >= 4 else digits,
        }
    
    def _mask_card_number(self, card_number: str) -> str:
        """Mask credit card number for safe display.
        
        Args:
            card_number: Credit card number
            
        Returns:
            Masked card number
        """
        if len(card_number) <= 4:
            return "*" * len(card_number)
        
        return "*" * (len(card_number) - 4) + card_number[-4:]
    
    def _get_detected_card_types(
        self, matches: List[Dict[str, Any]]
    ) -> List[str]:
        """Get list of detected credit card types.
        
        Args:
            matches: List of PCI matches
            
        Returns:
            List of unique card types detected
        """
        card_types = set()
        for match in matches:
            if (match["type"] == "CREDIT_CARD" and
                    "card_type" in match.get("metadata", {})):
                card_types.add(match["metadata"]["card_type"])
        
        return list(card_types)
    
    def _calculate_pci_risk_level(
        self, matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall PCI risk level.
        
        Args:
            matches: List of PCI matches
            
        Returns:
            Risk assessment dictionary
        """
        if not matches:
            return {"level": "none", "score": 0.0}
        
        # Risk weights for different PCI data types
        risk_weights = {
            "CREDIT_CARD": 1.0,
            "CVV": 1.0,
            "BANK_ACCOUNT": 0.9,
            "ROUTING_NUMBER": 0.8,
            "PIN": 0.9,
            "CARD_EXPIRY": 0.6,
            "IBAN": 0.8,
            "SWIFT_CODE": 0.5,
            "TRANSACTION_ID": 0.4,
        }
        
        total_risk = 0.0
        critical_data_found = False
        
        for match in matches:
            pci_type = match["type"]
            confidence = match["confidence"]
            weight = risk_weights.get(pci_type, 0.5)
            total_risk += weight * confidence
            
            # Flag critical data types
            if pci_type in ["CREDIT_CARD", "CVV", "BANK_ACCOUNT", "PIN"]:
                critical_data_found = True
        
        # Normalize risk score
        max_possible_risk = len(matches) * 1.0
        normalized_risk = min(1.0, total_risk / max(max_possible_risk, 1.0))
        
        # Boost risk if critical data found
        if critical_data_found:
            normalized_risk = min(1.0, normalized_risk * 1.2)
        
        # Determine risk level
        if normalized_risk >= 0.9 or critical_data_found:
            level = "critical"
        elif normalized_risk >= 0.7:
            level = "high"
        elif normalized_risk >= 0.4:
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
            "critical_data_found": critical_data_found,
        }
    
    def set_strict_validation(self, strict: bool) -> None:
        """Set strict validation mode.
        
        Args:
            strict: Whether to use strict validation
        """
        self.strict_validation = strict
        self.logger.info("Strict validation updated", strict=strict)
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the PCI detector.
        
        Returns:
            Dictionary containing detector information
        """
        return {
            "enabled": self.enabled,
            "strict_validation": self.strict_validation,
            "pattern_count": len(self.pattern_matcher.patterns),
            "supported_types": [
                "CREDIT_CARD", "BANK_ACCOUNT", "ROUTING_NUMBER", "CVV",
                "CARD_EXPIRY", "PIN", "IBAN", "SWIFT_CODE", "TRANSACTION_ID"
            ],
            "supported_card_types": list(self.card_types.values()),
        }
    
    def enable(self) -> None:
        """Enable the PCI detector."""
        self.enabled = True
        self.pattern_matcher.enable()
        self.logger.info("PCI detector enabled")
    
    def disable(self) -> None:
        """Disable the PCI detector."""
        self.enabled = False
        self.pattern_matcher.disable()
        self.logger.info("PCI detector disabled")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the PCI detector.
        
        Returns:
            Health check results
        """
        try:
            # Test with sample PCI data (using test card number)
            test_text = (
                "Card: 4111111111111111, CVV: 123, "
                "Exp: 12/25, Account: 1234567890"
            )
            result = self.analyze(test_text)
            
            return {
                "status": "healthy",
                "enabled": self.enabled,
                "strict_validation": self.strict_validation,
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