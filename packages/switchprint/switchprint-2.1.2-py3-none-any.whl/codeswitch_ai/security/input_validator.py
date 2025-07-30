#!/usr/bin/env python3
"""Input validation and sanitization for secure text processing."""

import re
import html
import unicodedata
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for validation."""
    PERMISSIVE = "permissive"
    MODERATE = "moderate"
    STRICT = "strict"
    PARANOID = "paranoid"


class ValidationStatus(Enum):
    """Validation result status."""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class ValidationResult:
    """Result of input validation."""
    status: ValidationStatus
    sanitized_text: str
    warnings: List[str]
    threats_detected: List[str]
    confidence_score: float
    original_length: int
    sanitized_length: int
    security_level: SecurityLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        result['security_level'] = self.security_level.value
        return result
    
    def is_safe(self) -> bool:
        """Check if input is considered safe."""
        return self.status in [ValidationStatus.PASSED, ValidationStatus.WARNING]
    
    @property
    def is_valid(self) -> bool:
        """Check if input is valid (alias for is_safe)."""
        return self.is_safe()


@dataclass
class SecurityConfig:
    """Security configuration for input validation."""
    security_level: SecurityLevel = SecurityLevel.MODERATE
    max_text_length: int = 10000
    max_line_length: int = 1000
    allowed_scripts: Optional[Set[str]] = None
    blocked_patterns: Optional[List[str]] = None
    enable_html_sanitization: bool = True
    enable_url_detection: bool = True
    enable_pii_detection: bool = True
    enable_injection_detection: bool = True
    log_security_events: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['security_level'] = self.security_level.value
        result['allowed_scripts'] = list(self.allowed_scripts) if self.allowed_scripts else None
        return result


class TextSanitizer:
    """Text sanitization utilities."""
    
    # Common injection patterns
    INJECTION_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # JavaScript
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=',                 # Event handlers
        r'<iframe[^>]*>.*?</iframe>',  # Iframes
        r'<object[^>]*>.*?</object>',  # Objects
        r'<embed[^>]*>',              # Embeds
        r'<link[^>]*>',               # Links
        r'<meta[^>]*>',               # Meta tags
        r'data:.*base64',             # Data URLs
        r'vbscript:',                 # VBScript
    ]
    
    # PII patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    }
    
    # URL patterns
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML content."""
        # Escape HTML entities
        sanitized = html.escape(text)
        
        # Remove potentially dangerous tags
        for pattern in TextSanitizer.INJECTION_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized
    
    @staticmethod
    def detect_pii(text: str) -> Dict[str, List[str]]:
        """Detect personally identifiable information."""
        detected_pii = {}
        
        for pii_type, pattern in TextSanitizer.PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_pii[pii_type] = matches
        
        return detected_pii
    
    @staticmethod
    def detect_urls(text: str) -> List[str]:
        """Detect URLs in text."""
        return re.findall(TextSanitizer.URL_PATTERN, text)
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalize unicode characters."""
        # Normalize to NFC form
        normalized = unicodedata.normalize('NFC', text)
        
        # Remove control characters except newlines and tabs
        cleaned = ''.join(
            char for char in normalized 
            if unicodedata.category(char) != 'Cc' or char in '\n\t'
        )
        
        return cleaned
    
    @staticmethod
    def detect_script_mixing(text: str) -> Dict[str, float]:
        """Detect script mixing that might indicate attacks."""
        script_counts = {}
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                script = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'UNKNOWN'
                script_counts[script] = script_counts.get(script, 0) + 1
                total_chars += 1
        
        if total_chars == 0:
            return {}
        
        # Calculate script ratios
        script_ratios = {
            script: count / total_chars 
            for script, count in script_counts.items()
        }
        
        return script_ratios


class InputValidator:
    """Comprehensive input validator for secure text processing."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize input validator.
        
        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.sanitizer = TextSanitizer()
        
        # Compile regex patterns for performance
        self._injection_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.sanitizer.INJECTION_PATTERNS
        ]
        
        # Custom blocked patterns
        self._blocked_patterns = []
        if self.config.blocked_patterns:
            self._blocked_patterns = [
                re.compile(pattern, re.IGNORECASE)
                for pattern in self.config.blocked_patterns
            ]
        
        logger.info(f"Input validator initialized with {self.config.security_level.value} security level")
    
    def validate(self, text: str, source: str = "unknown") -> ValidationResult:
        """Validate and sanitize input text.
        
        Args:
            text: Input text to validate
            source: Source identifier for logging
            
        Returns:
            Validation result with sanitized text and security assessment
        """
        if not isinstance(text, str):
            return ValidationResult(
                status=ValidationStatus.FAILED,
                sanitized_text="",
                warnings=[f"Input must be string, got {type(text)}"],
                threats_detected=["invalid_type"],
                confidence_score=0.0,
                original_length=0,
                sanitized_length=0,
                security_level=self.config.security_level
            )
        
        original_length = len(text)
        warnings = []
        threats = []
        
        # Length validation
        if original_length > self.config.max_text_length:
            if self.config.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                return ValidationResult(
                    status=ValidationStatus.BLOCKED,
                    sanitized_text="",
                    warnings=[],
                    threats_detected=["text_too_long"],
                    confidence_score=0.0,
                    original_length=original_length,
                    sanitized_length=0,
                    security_level=self.config.security_level
                )
            else:
                text = text[:self.config.max_text_length]
                warnings.append(f"Text truncated to {self.config.max_text_length} characters")
        
        # Line length validation
        lines = text.split('\n')
        if any(len(line) > self.config.max_line_length for line in lines):
            if self.config.security_level == SecurityLevel.PARANOID:
                threats.append("long_lines_detected")
            else:
                warnings.append("Long lines detected")
        
        # Start sanitization
        sanitized_text = text
        
        # Unicode normalization
        sanitized_text = self.sanitizer.normalize_unicode(sanitized_text)
        
        # HTML sanitization
        if self.config.enable_html_sanitization:
            original_html = sanitized_text
            sanitized_text = self.sanitizer.sanitize_html(sanitized_text)
            if sanitized_text != original_html:
                threats.append("html_content_sanitized")
        
        # Injection detection
        if self.config.enable_injection_detection:
            for pattern in self._injection_patterns:
                if pattern.search(sanitized_text):
                    threats.append("injection_pattern_detected")
                    # Remove the pattern in strict modes
                    if self.config.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                        sanitized_text = pattern.sub('', sanitized_text)
        
        # Custom blocked patterns
        for pattern in self._blocked_patterns:
            if pattern.search(sanitized_text):
                threats.append("blocked_pattern_detected")
                if self.config.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                    sanitized_text = pattern.sub('', sanitized_text)
        
        # URL detection
        if self.config.enable_url_detection:
            urls = self.sanitizer.detect_urls(sanitized_text)
            if urls:
                if self.config.security_level == SecurityLevel.PARANOID:
                    threats.append("urls_detected")
                    # Remove URLs in paranoid mode
                    sanitized_text = re.sub(self.sanitizer.URL_PATTERN, '[URL_REMOVED]', sanitized_text)
                else:
                    warnings.append(f"URLs detected: {len(urls)}")
        
        # PII detection
        if self.config.enable_pii_detection:
            pii_detected = self.sanitizer.detect_pii(sanitized_text)
            if pii_detected:
                if self.config.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                    threats.append("pii_detected")
                    # Anonymize PII
                    for pii_type, pattern in self.sanitizer.PII_PATTERNS.items():
                        if pii_type in pii_detected:
                            sanitized_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', sanitized_text)
                else:
                    warnings.append(f"PII detected: {list(pii_detected.keys())}")
        
        # Script mixing analysis
        script_ratios = self.sanitizer.detect_script_mixing(sanitized_text)
        if len(script_ratios) > 3:  # More than 3 different scripts
            if self.config.security_level == SecurityLevel.PARANOID:
                threats.append("excessive_script_mixing")
            else:
                warnings.append("Multiple scripts detected")
        
        # Script allowlist check
        if self.config.allowed_scripts:
            detected_scripts = set(script_ratios.keys())
            unauthorized_scripts = detected_scripts - self.config.allowed_scripts
            if unauthorized_scripts:
                if self.config.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                    threats.append("unauthorized_scripts")
                    # Filter out unauthorized characters
                    filtered_chars = []
                    for char in sanitized_text:
                        if char.isalpha():
                            script = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'UNKNOWN'
                            if script in self.config.allowed_scripts:
                                filtered_chars.append(char)
                        else:
                            filtered_chars.append(char)
                    sanitized_text = ''.join(filtered_chars)
                else:
                    warnings.append(f"Unauthorized scripts: {unauthorized_scripts}")
        
        # Determine final status
        if threats:
            if self.config.security_level == SecurityLevel.PARANOID:
                status = ValidationStatus.BLOCKED
            elif any(threat in ["injection_pattern_detected", "pii_detected"] for threat in threats):
                status = ValidationStatus.FAILED
            else:
                status = ValidationStatus.WARNING
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PASSED
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            threats, warnings, original_length, len(sanitized_text)
        )
        
        # Log security events
        if self.config.log_security_events and (threats or warnings):
            self._log_security_event(source, threats, warnings, original_length)
        
        return ValidationResult(
            status=status,
            sanitized_text=sanitized_text,
            warnings=warnings,
            threats_detected=threats,
            confidence_score=confidence_score,
            original_length=original_length,
            sanitized_length=len(sanitized_text),
            security_level=self.config.security_level
        )
    
    def _calculate_confidence_score(self, threats: List[str], warnings: List[str], 
                                  original_length: int, sanitized_length: int) -> float:
        """Calculate confidence score for validation result."""
        score = 1.0
        
        # Penalize threats more than warnings
        score -= len(threats) * 0.3
        score -= len(warnings) * 0.1
        
        # Penalize significant length changes
        if original_length > 0:
            length_change = abs(original_length - sanitized_length) / original_length
            score -= length_change * 0.2
        
        # Serious threats get lower scores
        serious_threats = ["injection_pattern_detected", "pii_detected", "blocked_pattern_detected"]
        if any(threat in serious_threats for threat in threats):
            score -= 0.5
        
        return max(0.0, min(1.0, score))
    
    def _log_security_event(self, source: str, threats: List[str], 
                          warnings: List[str], text_length: int) -> None:
        """Log security events for monitoring."""
        event_data = {
            'source': source,
            'threats': threats,
            'warnings': warnings,
            'text_length': text_length,
            'security_level': self.config.security_level.value,
            'timestamp': __import__('time').time()
        }
        
        if threats:
            logger.warning(f"Security threats detected from {source}: {threats}")
        if warnings:
            logger.info(f"Security warnings from {source}: {warnings}")
    
    def batch_validate(self, texts: List[str], sources: Optional[List[str]] = None) -> List[ValidationResult]:
        """Validate multiple texts in batch.
        
        Args:
            texts: List of texts to validate
            sources: Optional list of source identifiers
            
        Returns:
            List of validation results
        """
        if sources is None:
            sources = [f"batch_{i}" for i in range(len(texts))]
        
        results = []
        for text, source in zip(texts, sources):
            result = self.validate(text, source)
            results.append(result)
        
        return results
    
    def get_security_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate security summary from validation results.
        
        Args:
            results: List of validation results
            
        Returns:
            Security summary statistics
        """
        if not results:
            return {}
        
        summary = {
            'total_validations': len(results),
            'passed': sum(1 for r in results if r.status == ValidationStatus.PASSED),
            'warnings': sum(1 for r in results if r.status == ValidationStatus.WARNING),
            'failed': sum(1 for r in results if r.status == ValidationStatus.FAILED),
            'blocked': sum(1 for r in results if r.status == ValidationStatus.BLOCKED),
            'average_confidence': sum(r.confidence_score for r in results) / len(results),
            'common_threats': self._get_common_items([r.threats_detected for r in results]),
            'common_warnings': self._get_common_items([r.warnings for r in results]),
            'total_sanitization_savings': sum(
                r.original_length - r.sanitized_length for r in results
            )
        }
        
        return summary
    
    def _get_common_items(self, item_lists: List[List[str]]) -> Dict[str, int]:
        """Get common items from lists with counts."""
        all_items = []
        for item_list in item_lists:
            all_items.extend(item_list)
        
        item_counts = {}
        for item in all_items:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        # Return top 10 most common
        return dict(sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:10])


def main():
    """Example usage of input validation."""
    print("🔒 Input Validation Security Example")
    print("=" * 40)
    
    # Initialize validator with different security levels
    configs = [
        SecurityConfig(security_level=SecurityLevel.PERMISSIVE),
        SecurityConfig(security_level=SecurityLevel.MODERATE),
        SecurityConfig(security_level=SecurityLevel.STRICT),
    ]
    
    # Test cases with various security concerns
    test_cases = [
        "Hello, this is normal text",
        "Contact me at john.doe@email.com or call 555-123-4567",
        "<script>alert('XSS attack')</script>Hello world",
        "Visit https://suspicious-site.com for more info",
        "Mixed scripts: Hello 你好 مرحبا Здравствуйте",
        "Credit card: 4532 1234 5678 9012",
        "Long line: " + "A" * 2000,
        "JavaScript injection: <img src=x onerror=alert('hack')>",
    ]
    
    for i, config in enumerate(configs):
        print(f"\n--- Security Level: {config.security_level.value.upper()} ---")
        validator = InputValidator(config)
        
        for j, text in enumerate(test_cases[:3]):  # Test first 3 cases
            print(f"\nTest {j+1}: '{text[:50]}...'")
            result = validator.validate(text, f"test_{j}")
            
            print(f"  Status: {result.status.value}")
            print(f"  Confidence: {result.confidence_score:.3f}")
            print(f"  Threats: {result.threats_detected}")
            print(f"  Warnings: {result.warnings}")
            
            if result.sanitized_text != text:
                print(f"  Sanitized: '{result.sanitized_text[:50]}...'")
    
    print("\n✓ Input validation security example completed")


if __name__ == "__main__":
    main()