#!/usr/bin/env python3
"""Privacy protection and data anonymization for code-switching detection."""

import re
import hashlib
import uuid
import random
import string
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy protection levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class PIIType(Enum):
    """Types of personally identifiable information."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    ID_NUMBER = "id_number"
    MEDICAL_INFO = "medical_info"


@dataclass
class PrivacyConfig:
    """Configuration for privacy protection."""
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD
    enabled_detectors: Set[PIIType] = None
    anonymization_method: str = "replacement"  # replacement, hashing, masking
    preserve_language_structure: bool = True
    salt: Optional[str] = None
    
    def __post_init__(self):
        if self.enabled_detectors is None:
            self.enabled_detectors = {
                PIIType.EMAIL, PIIType.PHONE, PIIType.CREDIT_CARD, 
                PIIType.SSN, PIIType.IP_ADDRESS
            }
        
        if self.salt is None:
            self.salt = str(uuid.uuid4())


@dataclass
class PIIDetection:
    """Detected PII information."""
    pii_type: PIIType
    original_text: str
    start_position: int
    end_position: int
    confidence: float
    anonymized_replacement: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['pii_type'] = self.pii_type.value
        return result


class PIIDetector:
    """Detect personally identifiable information in text."""
    
    # Enhanced PII patterns
    PII_PATTERNS = {
        PIIType.EMAIL: {
            'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'confidence': 0.95
        },
        PIIType.PHONE: {
            'pattern': r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'confidence': 0.85
        },
        PIIType.SSN: {
            'pattern': r'\b\d{3}-\d{2}-\d{4}\b',
            'confidence': 0.99
        },
        PIIType.CREDIT_CARD: {
            'pattern': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'confidence': 0.90
        },
        PIIType.IP_ADDRESS: {
            'pattern': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'confidence': 0.80
        },
        PIIType.NAME: {
            'pattern': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'confidence': 0.60  # Lower confidence as it could be common words
        },
        PIIType.DATE_OF_BIRTH: {
            'pattern': r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
            'confidence': 0.70
        },
        PIIType.ID_NUMBER: {
            'pattern': r'\b[A-Z]{2}\d{6,12}\b',
            'confidence': 0.75
        }
    }
    
    # Medical/health-related patterns
    MEDICAL_PATTERNS = {
        'prescription': r'\b(?:prescription|rx|medication|dosage)\s+\w+',
        'diagnosis': r'\b(?:diagnosed with|suffers from|treatment for)\s+\w+',
        'medical_id': r'\b(?:patient|medical)\s+(?:id|number):\s*\w+'
    }
    
    def __init__(self, config: PrivacyConfig):
        """Initialize PII detector.
        
        Args:
            config: Privacy configuration
        """
        self.config = config
        
        # Compile patterns for performance
        self.compiled_patterns = {}
        for pii_type in self.config.enabled_detectors:
            if pii_type in self.PII_PATTERNS:
                pattern_info = self.PII_PATTERNS[pii_type]
                self.compiled_patterns[pii_type] = {
                    'regex': re.compile(pattern_info['pattern'], re.IGNORECASE),
                    'confidence': pattern_info['confidence']
                }
        
        # Compile medical patterns if enabled
        self.medical_patterns = {}
        if PIIType.MEDICAL_INFO in self.config.enabled_detectors:
            for name, pattern in self.MEDICAL_PATTERNS.items():
                self.medical_patterns[name] = re.compile(pattern, re.IGNORECASE)
    
    def detect_pii(self, text: str) -> List[PIIDetection]:
        """Detect PII in text.
        
        Args:
            text: Input text to scan
            
        Returns:
            List of detected PII instances
        """
        detections = []
        
        # Standard PII detection
        for pii_type, pattern_info in self.compiled_patterns.items():
            regex = pattern_info['regex']
            confidence = pattern_info['confidence']
            
            for match in regex.finditer(text):
                detection = PIIDetection(
                    pii_type=pii_type,
                    original_text=match.group(),
                    start_position=match.start(),
                    end_position=match.end(),
                    confidence=confidence,
                    anonymized_replacement=""  # Will be filled by anonymizer
                )
                detections.append(detection)
        
        # Medical information detection
        if PIIType.MEDICAL_INFO in self.config.enabled_detectors:
            for name, pattern in self.medical_patterns.items():
                for match in pattern.finditer(text):
                    detection = PIIDetection(
                        pii_type=PIIType.MEDICAL_INFO,
                        original_text=match.group(),
                        start_position=match.start(),
                        end_position=match.end(),
                        confidence=0.75,
                        anonymized_replacement=""
                    )
                    detections.append(detection)
        
        # Sort by position for proper replacement
        detections.sort(key=lambda x: x.start_position)
        
        return detections
    
    def is_likely_pii(self, text: str, threshold: float = 0.5) -> bool:
        """Check if text likely contains PII.
        
        Args:
            text: Text to check
            threshold: Confidence threshold
            
        Returns:
            True if PII is likely present
        """
        detections = self.detect_pii(text)
        return any(d.confidence >= threshold for d in detections)


class DataAnonymizer:
    """Anonymize detected PII while preserving text structure."""
    
    def __init__(self, config: PrivacyConfig):
        """Initialize data anonymizer.
        
        Args:
            config: Privacy configuration
        """
        self.config = config
        
        # Replacement templates
        self.replacement_templates = {
            PIIType.EMAIL: "[EMAIL_{}]",
            PIIType.PHONE: "[PHONE_{}]",
            PIIType.SSN: "[SSN_{}]",
            PIIType.CREDIT_CARD: "[CARD_{}]",
            PIIType.IP_ADDRESS: "[IP_{}]",
            PIIType.NAME: "[NAME_{}]",
            PIIType.ADDRESS: "[ADDRESS_{}]",
            PIIType.DATE_OF_BIRTH: "[DOB_{}]",
            PIIType.ID_NUMBER: "[ID_{}]",
            PIIType.MEDICAL_INFO: "[MEDICAL_{}]"
        }
        
        # Fake data generators for high-privacy scenarios
        self.fake_generators = {
            PIIType.EMAIL: self._generate_fake_email,
            PIIType.PHONE: self._generate_fake_phone,
            PIIType.NAME: self._generate_fake_name,
        }
    
    def anonymize_text(self, text: str, detections: List[PIIDetection]) -> Tuple[str, Dict[str, str]]:
        """Anonymize text based on PII detections.
        
        Args:
            text: Original text
            detections: List of PII detections
            
        Returns:
            Tuple of (anonymized_text, mapping_dict)
        """
        if not detections:
            return text, {}
        
        anonymized_text = text
        mapping = {}
        offset = 0
        
        # Process detections in reverse order to maintain positions
        for detection in reversed(detections):
            start_pos = detection.start_position
            end_pos = detection.end_position
            original = detection.original_text
            
            # Generate anonymized replacement
            replacement = self._generate_replacement(detection)
            detection.anonymized_replacement = replacement
            
            # Replace in text
            anonymized_text = (
                anonymized_text[:start_pos] + 
                replacement + 
                anonymized_text[end_pos:]
            )
            
            # Store mapping
            mapping[original] = replacement
        
        return anonymized_text, mapping
    
    def _generate_replacement(self, detection: PIIDetection) -> str:
        """Generate appropriate replacement for detected PII.
        
        Args:
            detection: PII detection instance
            
        Returns:
            Anonymized replacement string
        """
        pii_type = detection.pii_type
        original = detection.original_text
        
        if self.config.anonymization_method == "hashing":
            # Generate consistent hash-based replacement
            hash_input = f"{original}{self.config.salt}".encode()
            hash_hex = hashlib.sha256(hash_input).hexdigest()[:8]
            template = self.replacement_templates.get(pii_type, "[PII_{}]")
            return template.format(hash_hex.upper())
        
        elif self.config.anonymization_method == "masking":
            # Mask with asterisks, preserving structure
            if pii_type == PIIType.EMAIL:
                if "@" in original:
                    local, domain = original.split("@", 1)
                    masked_local = local[0] + "*" * (len(local) - 2) + local[-1] if len(local) > 2 else "***"
                    return f"{masked_local}@{domain}"
            elif pii_type == PIIType.PHONE:
                return re.sub(r'\d', '*', original)
            elif pii_type == PIIType.CREDIT_CARD:
                return "**** **** **** " + original[-4:] if len(original) >= 4 else "****"
            else:
                return "*" * len(original)
        
        elif self.config.anonymization_method == "replacement":
            # Use template-based replacement
            if self.config.privacy_level == PrivacyLevel.MAXIMUM and pii_type in self.fake_generators:
                # Generate realistic fake data
                return self.fake_generators[pii_type]()
            else:
                # Use generic templates
                template = self.replacement_templates.get(pii_type, "[PII_{}]")
                identifier = self._generate_consistent_id(original)
                return template.format(identifier)
        
        # Default fallback
        return "[REDACTED]"
    
    def _generate_consistent_id(self, original: str) -> str:
        """Generate consistent identifier for original text.
        
        Args:
            original: Original text
            
        Returns:
            Consistent identifier
        """
        hash_input = f"{original}{self.config.salt}".encode()
        hash_hex = hashlib.md5(hash_input).hexdigest()[:6]
        return hash_hex.upper()
    
    def _generate_fake_email(self) -> str:
        """Generate realistic fake email."""
        domains = ["example.com", "test.org", "sample.net"]
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def _generate_fake_phone(self) -> str:
        """Generate realistic fake phone number."""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"({area_code}) {exchange}-{number}"
    
    def _generate_fake_name(self) -> str:
        """Generate realistic fake name."""
        first_names = ["John", "Jane", "Alex", "Chris", "Taylor", "Jordan"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"


class PrivacyProtector:
    """Main privacy protection orchestrator."""
    
    def __init__(self, config: Optional[PrivacyConfig] = None):
        """Initialize privacy protector.
        
        Args:
            config: Privacy configuration
        """
        self.config = config or PrivacyConfig()
        self.detector = PIIDetector(self.config)
        self.anonymizer = DataAnonymizer(self.config)
        
        # Privacy audit log
        self.audit_log = []
        
        logger.info(f"Privacy protector initialized with {self.config.privacy_level.value} level")
    
    def protect_text(self, text: str, source_id: Optional[str] = None) -> Dict[str, Any]:
        """Apply privacy protection to text.
        
        Args:
            text: Input text to protect
            source_id: Optional source identifier for auditing
            
        Returns:
            Privacy protection result
        """
        if not isinstance(text, str):
            return {
                'protected_text': '',
                'pii_detected': [],
                'anonymization_mapping': {},
                'privacy_risk_score': 1.0,
                'protection_applied': False
            }
        
        # Detect PII
        detections = self.detector.detect_pii(text)
        
        # Apply anonymization if PII detected
        if detections:
            protected_text, mapping = self.anonymizer.anonymize_text(text, detections)
            protection_applied = True
        else:
            protected_text = text
            mapping = {}
            protection_applied = False
        
        # Calculate privacy risk score
        risk_score = self._calculate_privacy_risk(detections, text)
        
        # Create audit entry
        audit_entry = {
            'timestamp': __import__('time').time(),
            'source_id': source_id or 'unknown',
            'original_length': len(text),
            'protected_length': len(protected_text),
            'pii_count': len(detections),
            'risk_score': risk_score,
            'protection_applied': protection_applied
        }
        self.audit_log.append(audit_entry)
        
        # Log privacy events
        if detections:
            pii_types = [d.pii_type.value for d in detections]
            logger.warning(f"PII detected in {source_id}: {pii_types}")
        
        result = {
            'protected_text': protected_text,
            'pii_detected': [d.to_dict() for d in detections],
            'anonymization_mapping': mapping,
            'privacy_risk_score': risk_score,
            'protection_applied': protection_applied,
            'original_length': len(text),
            'protected_length': len(protected_text)
        }
        
        return result
    
    def batch_protect(self, texts: List[str], source_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Apply privacy protection to multiple texts.
        
        Args:
            texts: List of texts to protect
            source_ids: Optional list of source identifiers
            
        Returns:
            List of privacy protection results
        """
        if source_ids is None:
            source_ids = [f"batch_{i}" for i in range(len(texts))]
        
        results = []
        for text, source_id in zip(texts, source_ids):
            result = self.protect_text(text, source_id)
            results.append(result)
        
        return results
    
    def _calculate_privacy_risk(self, detections: List[PIIDetection], text: str) -> float:
        """Calculate privacy risk score for text.
        
        Args:
            detections: List of PII detections
            text: Original text
            
        Returns:
            Privacy risk score (0.0 to 1.0)
        """
        if not detections:
            return 0.0
        
        # Base risk from number of detections
        detection_risk = min(len(detections) * 0.2, 0.8)
        
        # Risk from PII types
        high_risk_types = {PIIType.SSN, PIIType.CREDIT_CARD, PIIType.MEDICAL_INFO}
        medium_risk_types = {PIIType.EMAIL, PIIType.PHONE, PIIType.ID_NUMBER}
        
        type_risk = 0.0
        for detection in detections:
            if detection.pii_type in high_risk_types:
                type_risk += 0.3
            elif detection.pii_type in medium_risk_types:
                type_risk += 0.2
            else:
                type_risk += 0.1
        
        type_risk = min(type_risk, 0.6)
        
        # Risk from confidence levels
        confidence_risk = max(d.confidence for d in detections) * 0.3
        
        # Combine risks
        total_risk = min(detection_risk + type_risk + confidence_risk, 1.0)
        
        return total_risk
    
    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate privacy protection report.
        
        Returns:
            Privacy report dictionary
        """
        if not self.audit_log:
            return {"message": "No privacy audit data available"}
        
        total_processed = len(self.audit_log)
        texts_with_pii = sum(1 for entry in self.audit_log if entry['pii_count'] > 0)
        total_pii_detected = sum(entry['pii_count'] for entry in self.audit_log)
        
        avg_risk_score = sum(entry['risk_score'] for entry in self.audit_log) / total_processed
        
        high_risk_texts = sum(1 for entry in self.audit_log if entry['risk_score'] > 0.7)
        
        report = {
            'summary': {
                'total_texts_processed': total_processed,
                'texts_with_pii': texts_with_pii,
                'total_pii_instances': total_pii_detected,
                'average_risk_score': avg_risk_score,
                'high_risk_texts': high_risk_texts,
                'protection_rate': texts_with_pii / total_processed if total_processed > 0 else 0
            },
            'configuration': self.config.to_dict() if hasattr(self.config, 'to_dict') else str(self.config),
            'audit_log_size': len(self.audit_log),
            'timestamp': __import__('time').time()
        }
        
        return report
    
    def clear_audit_log(self) -> None:
        """Clear the privacy audit log."""
        self.audit_log.clear()
        logger.info("Privacy audit log cleared")


def main():
    """Example usage of privacy protection."""
    print("🔒 Privacy Protection Example")
    print("=" * 40)
    
    # Test different privacy levels
    privacy_levels = [PrivacyLevel.STANDARD, PrivacyLevel.HIGH, PrivacyLevel.MAXIMUM]
    
    # Test cases with various PII
    test_cases = [
        "Contact John Doe at john.doe@email.com or call (555) 123-4567",
        "Patient ID: AB123456, DOB: 01/15/1980, SSN: 123-45-6789",
        "Credit card 4532 1234 5678 9012 expires next month",
        "Server logs show access from 192.168.1.100 at 10:30 AM",
        "Normal text without any PII information",
        "Mixed content: Call me at 555-0123 or email test@example.org"
    ]
    
    for i, level in enumerate(privacy_levels):
        print(f"\n--- Privacy Level: {level.value.upper()} ---")
        
        config = PrivacyConfig(
            privacy_level=level,
            anonymization_method="replacement" if level != PrivacyLevel.MAXIMUM else "replacement"
        )
        
        protector = PrivacyProtector(config)
        
        for j, text in enumerate(test_cases[:3]):  # Test first 3 cases
            print(f"\nTest {j+1}: '{text}'")
            
            result = protector.protect_text(text, f"test_{j}")
            
            print(f"  PII Detected: {len(result['pii_detected'])}")
            print(f"  Risk Score: {result['privacy_risk_score']:.3f}")
            print(f"  Protected: '{result['protected_text']}'")
            
            if result['pii_detected']:
                detected_types = [pii['pii_type'] for pii in result['pii_detected']]
                print(f"  PII Types: {detected_types}")
        
        # Generate privacy report
        report = protector.get_privacy_report()
        summary = report['summary']
        print(f"\nPrivacy Report:")
        print(f"  Texts with PII: {summary['texts_with_pii']}/{summary['total_texts_processed']}")
        print(f"  Average Risk: {summary['average_risk_score']:.3f}")
    
    print("\n✓ Privacy protection example completed")


if __name__ == "__main__":
    main()