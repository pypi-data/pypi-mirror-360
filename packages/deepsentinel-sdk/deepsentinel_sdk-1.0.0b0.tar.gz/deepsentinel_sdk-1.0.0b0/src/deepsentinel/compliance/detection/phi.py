"""PHI (Protected Health Information) detection module.

This module provides specialized detection for PHI data types including
medical record numbers, diagnosis codes, medication names, and other
health-related information as defined by HIPAA regulations.
"""

import re
from typing import Any, Dict, List, Optional

import structlog

from ...config import SentinelConfig
from .patterns import PatternMatcher


class PHIDetector:
    """Specialized detector for PHI data patterns.
    
    This detector focuses on identifying protected health information
    including medical records, diagnosis codes, medications, and other
    healthcare-related sensitive data.
    
    Attributes:
        config: Sentinel configuration
        pattern_matcher: Base pattern matcher
        enabled: Whether the detector is enabled
        medical_terms: Set of medical terminology for context analysis
        logger: Structured logger
    """
    
    def __init__(self, config: SentinelConfig) -> None:
        """Initialize the PHI detector.
        
        Args:
            config: Sentinel configuration
        """
        self.config = config
        self.enabled = True
        self.logger = structlog.get_logger(__name__)
        
        # Initialize pattern matcher with PHI-specific patterns
        self.pattern_matcher = PatternMatcher(config)
        self._load_phi_patterns()
        
        # Load medical terminology for enhanced detection
        self.medical_terms = self._load_medical_terms()
        
        self.logger.info(
            "PHI detector initialized",
            patterns=len(self.pattern_matcher.patterns),
            medical_terms=len(self.medical_terms),
        )
    
    def _load_phi_patterns(self) -> None:
        """Load PHI-specific detection patterns."""
        phi_patterns = {
            # Medical Record Numbers
            "medical_record_number": {
                "pattern": (
                    r"\b(?:MRN|MEDICAL.?RECORD|PATIENT.?ID|"
                    r"CHART.?NUMBER)[:\s#]*[A-Z0-9]{6,12}\b"
                ),
                "type": "MEDICAL_RECORD",
                "confidence": 0.9,
                "flags": re.IGNORECASE,
            },
            # Health Insurance Numbers
            "health_insurance": {
                "pattern": (
                    r"\b(?:INSURANCE|POLICY|MEMBER)[:\s#]*"
                    r"[A-Z0-9]{8,15}\b"
                ),
                "type": "HEALTH_INSURANCE",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # ICD-10 Diagnosis Codes
            "icd10_codes": {
                "pattern": (
                    r"\b[A-Z]\d{2}(?:\.\d{1,4})?\b"
                ),
                "type": "DIAGNOSIS_CODE",
                "confidence": 0.7,
                "flags": 0,
            },
            # CPT Procedure Codes
            "cpt_codes": {
                "pattern": (
                    r"\b(?:CPT|PROCEDURE)[:\s#]*\d{5}\b"
                ),
                "type": "PROCEDURE_CODE",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Prescription/RX Numbers
            "prescription_number": {
                "pattern": (
                    r"\b(?:RX|PRESCRIPTION)[:\s#]*[A-Z0-9]{6,12}\b"
                ),
                "type": "PRESCRIPTION",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Lab Test Results (basic pattern)
            "lab_results": {
                "pattern": (
                    r"\b(?:LAB|TEST|RESULT)[:\s]*"
                    r"(?:POSITIVE|NEGATIVE|ABNORMAL|NORMAL|"
                    r"\d+\.?\d*\s*(?:mg/dL|mmol/L|%|U/L))\b"
                ),
                "type": "LAB_RESULT",
                "confidence": 0.7,
                "flags": re.IGNORECASE,
            },
            # Provider Numbers (NPI)
            "provider_npi": {
                "pattern": (
                    r"\b(?:NPI|PROVIDER)[:\s#]*\d{10}\b"
                ),
                "type": "PROVIDER_ID",
                "confidence": 0.9,
                "flags": re.IGNORECASE,
            },
            # Hospital/Facility IDs
            "facility_id": {
                "pattern": (
                    r"\b(?:FACILITY|HOSPITAL)[:\s#]*[A-Z0-9]{4,10}\b"
                ),
                "type": "FACILITY_ID",
                "confidence": 0.7,
                "flags": re.IGNORECASE,
            },
            # Date patterns in medical context
            "medical_dates": {
                "pattern": (
                    r"\b(?:ADMISSION|DISCHARGE|VISIT|PROCEDURE)[:\s]*"
                    r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
                    r"\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b"
                ),
                "type": "MEDICAL_DATE",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
            # Medication dosages
            "medication_dosage": {
                "pattern": (
                    r"\b\d+\.?\d*\s*(?:mg|mcg|g|mL|tablets?|pills?|"
                    r"capsules?)\s+(?:daily|twice|once|BID|TID|QID)\b"
                ),
                "type": "MEDICATION",
                "confidence": 0.8,
                "flags": re.IGNORECASE,
            },
        }
        
        # Add patterns to matcher
        for name, pattern_info in phi_patterns.items():
            self.pattern_matcher.add_pattern(
                name=name,
                pattern=pattern_info["pattern"],
                pattern_type=pattern_info["type"],
                confidence=pattern_info["confidence"],
                flags=pattern_info.get("flags", 0),
            )
    
    def _load_medical_terms(self) -> set:
        """Load common medical terms for context analysis.
        
        Returns:
            Set of medical terms
        """
        medical_terms = {
            # Medical specialties
            "cardiology", "neurology", "oncology", "pediatrics", "psychiatry",
            "radiology", "surgery", "emergency", "internal medicine",
            
            # Medical conditions
            "diabetes", "hypertension", "cancer", "pneumonia", "asthma",
            "depression", "anxiety", "heart disease", "stroke", "infection",
            
            # Medical procedures
            "surgery", "biopsy", "endoscopy", "ultrasound", "mri", "ct scan",
            "x-ray", "blood test", "urine test", "ecg", "ekg",
            
            # Medical terms
            "patient", "diagnosis", "treatment", "medication", "prescription",
            "symptoms", "examination", "consultation", "admission",
            "discharge",
            "medical", "clinical", "therapeutic", "diagnostic", "prognosis",
            
            # Body parts and systems
            "heart", "lung", "liver", "kidney", "brain", "blood", "bone",
            "muscle", "nerve", "skin", "eye", "ear", "nose", "throat",
            
            # Medical measurements
            "blood pressure", "heart rate", "temperature", "weight", "height",
            "glucose", "cholesterol", "hemoglobin", "platelet",
            "white blood cell",
        }
        
        return medical_terms
    
    def analyze(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text for PHI patterns.
        
        Args:
            text: Text to analyze
            context: Optional context information
            
        Returns:
            Dictionary containing PHI detection results
        """
        if not self.enabled or not text.strip():
            return {"matches": [], "phi_types": [], "medical_context": False}
        
        context = context or {}
        
        # Check if text has medical context
        medical_context = self._has_medical_context(text)
        
        # Run base pattern matching
        pattern_results = self.pattern_matcher.analyze(text, context)
        matches = []
        
        # Process matches with PHI-specific validation
        for match_dict in pattern_results.get("matches", []):
            phi_match = self._process_phi_match(
                match_dict, text, medical_context
            )
            if phi_match:
                matches.append(phi_match)
        
        # Additional medical term detection if in medical context
        if medical_context:
            term_matches = self._detect_medical_terms(text)
            matches.extend(term_matches)
        
        # Calculate risk assessment
        risk_assessment = self._calculate_phi_risk_level(
            matches, medical_context
        )
        
        # Get unique PHI types found
        phi_types = list(set(match["type"] for match in matches))
        
        return {
            "matches": matches,
            "phi_types": phi_types,
            "total_matches": len(matches),
            "medical_context": medical_context,
            "risk_level": risk_assessment["level"],
            "risk_score": risk_assessment["score"],
            "high_confidence_matches": len([
                m for m in matches if m["confidence"] >= 0.8
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
            Dictionary containing PHI detection results
        """
        return self.analyze(text, context)
    
    def _has_medical_context(self, text: str) -> bool:
        """Determine if text has medical context.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears to be medical in nature
        """
        text_lower = text.lower()
        medical_term_count = 0
        
        # Count medical terms in text
        for term in self.medical_terms:
            if term in text_lower:
                medical_term_count += 1
        
        # Consider medical context if multiple medical terms found
        return medical_term_count >= 2
    
    def _process_phi_match(
        self,
        match_dict: Dict[str, Any],
        full_text: str,
        medical_context: bool,
    ) -> Optional[Dict[str, Any]]:
        """Process and validate a PHI match.
        
        Args:
            match_dict: Raw pattern match dictionary
            full_text: Full text being analyzed
            medical_context: Whether text has medical context
            
        Returns:
            Processed PHI match or None if invalid
        """
        phi_type = match_dict["type"]
        match_text = match_dict["text"]
        
        # Boost confidence if in medical context
        confidence_boost = 0.1 if medical_context else 0.0
        adjusted_confidence = min(
            1.0, match_dict["confidence"] + confidence_boost
        )
        
        # Apply PHI-specific validation
        if not self._validate_phi_match(match_text, phi_type, medical_context):
            return None
        
        return {
            "text": match_text,
            "type": phi_type,
            "start": match_dict["start"],
            "end": match_dict["end"],
            "confidence": adjusted_confidence,
            "pattern_name": match_dict["pattern_name"],
            "metadata": {
                **match_dict.get("metadata", {}),
                "medical_context": medical_context,
                "original_confidence": match_dict["confidence"],
                "validation_passed": True,
            },
        }
    
    def _validate_phi_match(
        self, match_text: str, phi_type: str, medical_context: bool
    ) -> bool:
        """Validate PHI match using type-specific rules.
        
        Args:
            match_text: Matched text
            phi_type: Type of PHI
            medical_context: Whether in medical context
            
        Returns:
            True if valid, False otherwise
        """
        # ICD-10 code validation
        if phi_type == "DIAGNOSIS_CODE":
            return self._validate_icd10_code(match_text)
        
        # NPI validation
        elif phi_type == "PROVIDER_ID":
            return self._validate_npi(match_text)
        
        # Medical record number validation
        elif phi_type == "MEDICAL_RECORD":
            return medical_context  # Only valid in medical context
        
        # Lab result validation
        elif phi_type == "LAB_RESULT":
            return medical_context and self._validate_lab_result(match_text)
        
        # Default validation - require medical context for medical types
        medical_types = {
            "HEALTH_INSURANCE", "PRESCRIPTION", "PROCEDURE_CODE",
            "FACILITY_ID", "MEDICAL_DATE", "MEDICATION"
        }
        
        if phi_type in medical_types:
            return medical_context
        
        return True
    
    def _validate_icd10_code(self, code: str) -> bool:
        """Validate ICD-10 diagnosis code format.
        
        Args:
            code: ICD-10 code to validate
            
        Returns:
            True if valid format, False otherwise
        """
        # Basic ICD-10 format validation
        pattern = re.compile(r'^[A-Z]\d{2}(?:\.\d{1,4})?$')
        if not pattern.match(code):
            return False
        
        # Check for valid first character ranges
        first_char = code[0]
        valid_ranges = [
            ('A', 'B'),  # Infectious diseases
            ('C', 'D'),  # Neoplasms
            ('E', 'E'),  # Endocrine diseases
            ('F', 'F'),  # Mental disorders
            ('G', 'G'),  # Nervous system
            ('H', 'H'),  # Eye and ear
            ('I', 'I'),  # Circulatory system
            ('J', 'J'),  # Respiratory system
            ('K', 'K'),  # Digestive system
            ('L', 'L'),  # Skin
            ('M', 'M'),  # Musculoskeletal
            ('N', 'N'),  # Genitourinary
            ('O', 'O'),  # Pregnancy
            ('P', 'P'),  # Perinatal
            ('Q', 'Q'),  # Congenital
            ('R', 'R'),  # Symptoms
            ('S', 'T'),  # Injury
            ('V', 'Y'),  # External causes
            ('Z', 'Z'),  # Health status
        ]
        
        return any(start <= first_char <= end for start, end in valid_ranges)
    
    def _validate_npi(self, npi: str) -> bool:
        """Validate NPI (National Provider Identifier) number.
        
        Args:
            npi: NPI number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = re.sub(r'\D', '', npi)
        
        # NPI must be exactly 10 digits
        if len(digits) != 10:
            return False
        
        # NPI uses Luhn algorithm for validation
        return self._luhn_check(digits)
    
    def _validate_lab_result(self, result: str) -> bool:
        """Validate lab result format.
        
        Args:
            result: Lab result to validate
            
        Returns:
            True if valid format, False otherwise
        """
        result_lower = result.lower()
        
        # Check for valid result types
        valid_results = [
            "positive", "negative", "abnormal", "normal",
            "high", "low", "critical", "borderline"
        ]
        
        # Check for numeric results with units
        numeric_pattern = re.compile(r'\d+\.?\d*\s*(?:mg/dL|mmol/L|%|U/L)')
        
        return (any(term in result_lower for term in valid_results) or
                numeric_pattern.search(result))
    
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
    
    def _detect_medical_terms(self, text: str) -> List[Dict[str, Any]]:
        """Detect medical terminology in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of medical term matches
        """
        matches = []
        text_lower = text.lower()
        
        for term in self.medical_terms:
            # Find all occurrences of the term
            start = 0
            while True:
                pos = text_lower.find(term, start)
                if pos == -1:
                    break
                
                # Check word boundaries
                if ((pos == 0 or not text_lower[pos - 1].isalnum()) and
                        (pos + len(term) == len(text_lower) or
                         not text_lower[pos + len(term)].isalnum())):
                    
                    matches.append({
                        "text": text[pos:pos + len(term)],
                        "type": "MEDICAL_TERM",
                        "start": pos,
                        "end": pos + len(term),
                        "confidence": 0.6,
                        "pattern_name": "medical_terminology",
                        "metadata": {
                            "term": term,
                            "category": "medical_terminology",
                        },
                    })
                
                start = pos + 1
        
        return matches
    
    def _calculate_phi_risk_level(
        self, matches: List[Dict[str, Any]], medical_context: bool
    ) -> Dict[str, Any]:
        """Calculate overall PHI risk level.
        
        Args:
            matches: List of PHI matches
            medical_context: Whether text has medical context
            
        Returns:
            Risk assessment dictionary
        """
        if not matches:
            return {"level": "none", "score": 0.0}
        
        # Risk weights for different PHI types
        risk_weights = {
            "MEDICAL_RECORD": 1.0,
            "HEALTH_INSURANCE": 0.9,
            "DIAGNOSIS_CODE": 0.8,
            "PROCEDURE_CODE": 0.8,
            "PRESCRIPTION": 0.7,
            "LAB_RESULT": 0.9,
            "PROVIDER_ID": 0.6,
            "FACILITY_ID": 0.5,
            "MEDICAL_DATE": 0.4,
            "MEDICATION": 0.7,
            "MEDICAL_TERM": 0.3,
        }
        
        total_risk = 0.0
        for match in matches:
            phi_type = match["type"]
            confidence = match["confidence"]
            weight = risk_weights.get(phi_type, 0.5)
            total_risk += weight * confidence
        
        # Boost risk if in clear medical context
        if medical_context:
            total_risk *= 1.2
        
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
            "medical_context": medical_context,
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the PHI detector.
        
        Returns:
            Dictionary containing detector information
        """
        return {
            "enabled": self.enabled,
            "pattern_count": len(self.pattern_matcher.patterns),
            "medical_terms": len(self.medical_terms),
            "supported_types": [
                "MEDICAL_RECORD", "HEALTH_INSURANCE", "DIAGNOSIS_CODE",
                "PROCEDURE_CODE", "PRESCRIPTION", "LAB_RESULT",
                "PROVIDER_ID", "FACILITY_ID", "MEDICAL_DATE",
                "MEDICATION", "MEDICAL_TERM"
            ],
        }
    
    def enable(self) -> None:
        """Enable the PHI detector."""
        self.enabled = True
        self.pattern_matcher.enable()
        self.logger.info("PHI detector enabled")
    
    def disable(self) -> None:
        """Disable the PHI detector."""
        self.enabled = False
        self.pattern_matcher.disable()
        self.logger.info("PHI detector disabled")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the PHI detector.
        
        Returns:
            Health check results
        """
        try:
            # Test with sample PHI data
            test_text = (
                "Patient MRN: ABC123456, Diagnosis: E11.9 diabetes, "
                "Lab result: glucose 150 mg/dL"
            )
            result = self.analyze(test_text)
            
            return {
                "status": "healthy",
                "enabled": self.enabled,
                "test_matches": result["total_matches"],
                "medical_context_detected": result["medical_context"],
                "pattern_matcher_status": (
                    self.pattern_matcher.health_check()["status"]
                ),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }