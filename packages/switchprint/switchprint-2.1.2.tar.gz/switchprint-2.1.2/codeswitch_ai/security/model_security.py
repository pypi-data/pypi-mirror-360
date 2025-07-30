#!/usr/bin/env python3
"""Model security auditing and integrity checking."""

import hashlib
import os
import pickle
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityThreatLevel(Enum):
    """Security threat levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModelSecurityIssue(Enum):
    """Types of model security issues."""
    INTEGRITY_VIOLATION = "integrity_violation"
    SUSPICIOUS_PICKLE = "suspicious_pickle"
    UNTRUSTED_SOURCE = "untrusted_source"
    OVERSIZED_MODEL = "oversized_model"
    MALFORMED_DATA = "malformed_data"
    UNSAFE_OPERATIONS = "unsafe_operations"
    MEMORY_EXHAUSTION = "memory_exhaustion"
    DESERIALIZATION_RISK = "deserialization_risk"


@dataclass
class SecurityScanResult:
    """Result of model security scan."""
    model_path: str
    is_safe: bool
    threat_level: SecurityThreatLevel
    issues_detected: List[ModelSecurityIssue]
    warnings: List[str]
    file_hash: str
    file_size: int
    scan_timestamp: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['threat_level'] = self.threat_level.value
        result['issues_detected'] = [issue.value for issue in self.issues_detected]
        return result


class ModelIntegrityChecker:
    """Check model file integrity and authenticity."""
    
    def __init__(self):
        """Initialize integrity checker."""
        # Known safe model hashes (would be populated with verified models)
        self.trusted_hashes = set()
        
        # Known unsafe patterns
        self.unsafe_patterns = {
            'suspicious_pickle_ops': [
                b'__reduce__',
                b'__reduce_ex__',
                b'__setstate__',
                b'__getstate__',
                b'eval(',
                b'exec(',
                b'compile(',
                b'__import__',
                b'os.system',
                b'subprocess'
            ],
            'risky_modules': [
                b'builtins',
                b'sys',
                b'os',
                b'subprocess',
                b'importlib',
                b'__builtin__'
            ]
        }
        
        # Size limits (in bytes)
        self.max_model_size = 5 * 1024 * 1024 * 1024  # 5GB
        self.warn_model_size = 1 * 1024 * 1024 * 1024  # 1GB
    
    def calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash for integrity checking.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use
            
        Returns:
            Hexadecimal hash string
        """
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def check_file_integrity(self, file_path: str, expected_hash: Optional[str] = None) -> bool:
        """Check file integrity against expected hash.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            
        Returns:
            True if integrity check passes
        """
        if not os.path.exists(file_path):
            return False
        
        if expected_hash:
            actual_hash = self.calculate_file_hash(file_path)
            return actual_hash == expected_hash
        
        # If no expected hash, just verify file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)  # Try to read first byte
            return True
        except Exception:
            return False
    
    def scan_pickle_file(self, file_path: str) -> List[ModelSecurityIssue]:
        """Scan pickle file for security issues.
        
        Args:
            file_path: Path to pickle file
            
        Returns:
            List of detected security issues
        """
        issues = []
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Check for suspicious patterns
            for pattern_type, patterns in self.unsafe_patterns.items():
                for pattern in patterns:
                    if pattern in content:
                        if pattern_type == 'suspicious_pickle_ops':
                            issues.append(ModelSecurityIssue.SUSPICIOUS_PICKLE)
                        elif pattern_type == 'risky_modules':
                            issues.append(ModelSecurityIssue.UNSAFE_OPERATIONS)
                        break
            
            # Check for potential deserialization bombs
            if len(content) > self.max_model_size:
                issues.append(ModelSecurityIssue.MEMORY_EXHAUSTION)
            
            # Try to analyze pickle structure (safely)
            try:
                # Use pickletools to analyze without executing
                import pickletools
                import io
                
                pickle_analysis = io.StringIO()
                pickletools.dis(content, pickle_analysis)
                analysis_result = pickle_analysis.getvalue()
                
                # Look for suspicious operations in disassembly
                if any(op in analysis_result.lower() for op in ['reduce', 'global', 'build']):
                    issues.append(ModelSecurityIssue.DESERIALIZATION_RISK)
                    
            except Exception:
                # If we can't analyze safely, flag as risky
                issues.append(ModelSecurityIssue.MALFORMED_DATA)
        
        except Exception as e:
            logger.error(f"Failed to scan pickle file {file_path}: {e}")
            issues.append(ModelSecurityIssue.MALFORMED_DATA)
        
        return issues
    
    def validate_model_source(self, file_path: str, trusted_sources: Optional[List[str]] = None) -> bool:
        """Validate if model comes from trusted source.
        
        Args:
            file_path: Path to model file
            trusted_sources: List of trusted source identifiers
            
        Returns:
            True if source is trusted
        """
        if not trusted_sources:
            # If no trusted sources specified, assume local files are ok
            return os.path.dirname(os.path.abspath(file_path)).startswith(os.getcwd())
        
        file_hash = self.calculate_file_hash(file_path)
        
        # Check against known trusted hashes
        if file_hash in self.trusted_hashes:
            return True
        
        # Additional source validation logic could go here
        # (e.g., check digital signatures, download sources, etc.)
        
        return False


class ModelSecurityAuditor:
    """Comprehensive model security auditing."""
    
    def __init__(self, trusted_sources: Optional[List[str]] = None):
        """Initialize model security auditor.
        
        Args:
            trusted_sources: List of trusted model sources
        """
        self.integrity_checker = ModelIntegrityChecker()
        self.trusted_sources = trusted_sources or []
        self.scan_history = []
    
    def audit_model_file(self, file_path: str, expected_hash: Optional[str] = None) -> SecurityScanResult:
        """Perform comprehensive security audit of model file.
        
        Args:
            file_path: Path to model file
            expected_hash: Optional expected file hash
            
        Returns:
            Security scan result
        """
        logger.info(f"Starting security audit of {file_path}")
        
        issues = []
        warnings = []
        recommendations = []
        
        # Check if file exists
        if not os.path.exists(file_path):
            return SecurityScanResult(
                model_path=file_path,
                is_safe=False,
                threat_level=SecurityThreatLevel.HIGH,
                issues_detected=[ModelSecurityIssue.MALFORMED_DATA],
                warnings=["File does not exist"],
                file_hash="",
                file_size=0,
                scan_timestamp=time.time(),
                recommendations=["Verify file path and availability"]
            )
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_hash = self.integrity_checker.calculate_file_hash(file_path)
        
        # Size checks
        if file_size > self.integrity_checker.max_model_size:
            issues.append(ModelSecurityIssue.OVERSIZED_MODEL)
            recommendations.append("Consider model compression or splitting")
        elif file_size > self.integrity_checker.warn_model_size:
            warnings.append(f"Large model file ({file_size / (1024*1024):.1f} MB)")
        
        # Integrity check
        if expected_hash:
            if not self.integrity_checker.check_file_integrity(file_path, expected_hash):
                issues.append(ModelSecurityIssue.INTEGRITY_VIOLATION)
                recommendations.append("Verify model source and re-download if necessary")
        
        # Source validation
        if not self.integrity_checker.validate_model_source(file_path, self.trusted_sources):
            issues.append(ModelSecurityIssue.UNTRUSTED_SOURCE)
            warnings.append("Model source is not in trusted sources list")
            recommendations.append("Verify model authenticity before use")
        
        # File type specific checks
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.pkl', '.pickle']:
            pickle_issues = self.integrity_checker.scan_pickle_file(file_path)
            issues.extend(pickle_issues)
            if pickle_issues:
                recommendations.append("Consider using safer serialization formats (e.g., SafeTensors)")
        
        elif file_ext in ['.bin', '.pt', '.pth']:
            # PyTorch model checks
            try:
                # Try to inspect without loading
                with open(file_path, 'rb') as f:
                    header = f.read(1024)
                    if b'torch' not in header and b'pytorch' not in header:
                        warnings.append("File may not be a valid PyTorch model")
            except Exception:
                issues.append(ModelSecurityIssue.MALFORMED_DATA)
        
        elif file_ext in ['.h5', '.hdf5']:
            # HDF5/Keras model checks
            try:
                import h5py
                with h5py.File(file_path, 'r') as f:
                    # Basic validation that it's a proper HDF5 file
                    pass
            except Exception:
                issues.append(ModelSecurityIssue.MALFORMED_DATA)
                recommendations.append("Verify HDF5 file integrity")
        
        # Determine threat level
        threat_level = self._assess_threat_level(issues)
        
        # Determine if safe to use
        is_safe = threat_level in [SecurityThreatLevel.LOW, SecurityThreatLevel.MEDIUM]
        
        if not is_safe:
            recommendations.append("Do not use this model in production environments")
        
        # Create result
        result = SecurityScanResult(
            model_path=file_path,
            is_safe=is_safe,
            threat_level=threat_level,
            issues_detected=issues,
            warnings=warnings,
            file_hash=file_hash,
            file_size=file_size,
            scan_timestamp=time.time(),
            recommendations=recommendations
        )
        
        # Store in history
        self.scan_history.append(result)
        
        logger.info(f"Security audit completed: {threat_level.value} threat level")
        return result
    
    def _assess_threat_level(self, issues: List[ModelSecurityIssue]) -> SecurityThreatLevel:
        """Assess overall threat level based on detected issues.
        
        Args:
            issues: List of detected security issues
            
        Returns:
            Overall threat level
        """
        if not issues:
            return SecurityThreatLevel.LOW
        
        # Critical issues
        critical_issues = [
            ModelSecurityIssue.SUSPICIOUS_PICKLE,
            ModelSecurityIssue.UNSAFE_OPERATIONS,
            ModelSecurityIssue.DESERIALIZATION_RISK
        ]
        
        if any(issue in critical_issues for issue in issues):
            return SecurityThreatLevel.CRITICAL
        
        # High severity issues
        high_issues = [
            ModelSecurityIssue.INTEGRITY_VIOLATION,
            ModelSecurityIssue.MEMORY_EXHAUSTION,
            ModelSecurityIssue.MALFORMED_DATA
        ]
        
        if any(issue in high_issues for issue in issues):
            return SecurityThreatLevel.HIGH
        
        # Medium severity issues
        medium_issues = [
            ModelSecurityIssue.UNTRUSTED_SOURCE,
            ModelSecurityIssue.OVERSIZED_MODEL
        ]
        
        if any(issue in medium_issues for issue in issues):
            return SecurityThreatLevel.MEDIUM
        
        return SecurityThreatLevel.LOW
    
    def audit_multiple_models(self, model_paths: List[str]) -> List[SecurityScanResult]:
        """Audit multiple model files.
        
        Args:
            model_paths: List of model file paths
            
        Returns:
            List of security scan results
        """
        results = []
        for path in model_paths:
            result = self.audit_model_file(path)
            results.append(result)
        
        return results
    
    def generate_security_report(self, results: Optional[List[SecurityScanResult]] = None) -> Dict[str, Any]:
        """Generate comprehensive security report.
        
        Args:
            results: Optional list of scan results (uses scan history if not provided)
            
        Returns:
            Security report dictionary
        """
        if results is None:
            results = self.scan_history
        
        if not results:
            return {"message": "No scan results available"}
        
        # Aggregate statistics
        total_scans = len(results)
        safe_models = sum(1 for r in results if r.is_safe)
        unsafe_models = total_scans - safe_models
        
        # Threat level distribution
        threat_distribution = {}
        for level in SecurityThreatLevel:
            count = sum(1 for r in results if r.threat_level == level)
            threat_distribution[level.value] = count
        
        # Common issues
        all_issues = []
        for result in results:
            all_issues.extend(result.issues_detected)
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue.value] = issue_counts.get(issue.value, 0) + 1
        
        # Common warnings
        all_warnings = []
        for result in results:
            all_warnings.extend(result.warnings)
        
        warning_counts = {}
        for warning in all_warnings:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1
        
        report = {
            'scan_summary': {
                'total_models_scanned': total_scans,
                'safe_models': safe_models,
                'unsafe_models': unsafe_models,
                'safety_percentage': (safe_models / total_scans * 100) if total_scans > 0 else 0
            },
            'threat_level_distribution': threat_distribution,
            'common_issues': dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)),
            'common_warnings': dict(sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)),
            'recommendations': self._generate_global_recommendations(results),
            'scan_timestamp': time.time()
        }
        
        return report
    
    def _generate_global_recommendations(self, results: List[SecurityScanResult]) -> List[str]:
        """Generate global security recommendations based on scan results.
        
        Args:
            results: List of scan results
            
        Returns:
            List of security recommendations
        """
        recommendations = []
        
        # Check for patterns in results
        has_pickle_issues = any(
            ModelSecurityIssue.SUSPICIOUS_PICKLE in r.issues_detected 
            for r in results
        )
        
        has_untrusted_sources = any(
            ModelSecurityIssue.UNTRUSTED_SOURCE in r.issues_detected 
            for r in results
        )
        
        has_large_models = any(
            ModelSecurityIssue.OVERSIZED_MODEL in r.issues_detected 
            for r in results
        )
        
        if has_pickle_issues:
            recommendations.append("Consider migrating from pickle to safer serialization formats")
            recommendations.append("Implement strict pickle loading policies")
        
        if has_untrusted_sources:
            recommendations.append("Establish a trusted model registry")
            recommendations.append("Implement model signing and verification")
        
        if has_large_models:
            recommendations.append("Implement model compression strategies")
            recommendations.append("Consider model splitting for large architectures")
        
        # General recommendations
        recommendations.extend([
            "Regularly audit model security",
            "Keep model integrity hashes up to date",
            "Monitor model usage in production",
            "Implement access controls for model files"
        ])
        
        return recommendations


def main():
    """Example usage of model security auditing."""
    print("🔒 Model Security Audit Example")
    print("=" * 40)
    
    # Initialize auditor
    auditor = ModelSecurityAuditor()
    
    # For demo purposes, let's audit some common file types
    # (These files may not exist in the actual environment)
    demo_files = [
        "model.pkl",
        "model.bin", 
        "model.h5",
        "suspicious_model.pkl"
    ]
    
    print("\n🔍 Running security audits:")
    
    results = []
    for file_path in demo_files:
        print(f"\nAuditing: {file_path}")
        
        # Create a dummy file for demo if it doesn't exist
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'wb') as f:
                    f.write(b"dummy model data for security testing")
                print(f"  Created dummy file for testing")
            except Exception:
                print(f"  Skipped - cannot create test file")
                continue
        
        # Perform audit
        result = auditor.audit_model_file(file_path)
        results.append(result)
        
        print(f"  Threat Level: {result.threat_level.value}")
        print(f"  Safe to Use: {result.is_safe}")
        print(f"  Issues: {[issue.value for issue in result.issues_detected]}")
        print(f"  File Size: {result.file_size} bytes")
        print(f"  File Hash: {result.file_hash[:16]}...")
        
        # Clean up dummy file
        try:
            os.remove(file_path)
        except Exception:
            pass
    
    # Generate security report
    if results:
        print("\n📊 Security Report:")
        report = auditor.generate_security_report(results)
        
        summary = report['scan_summary']
        print(f"  Models Scanned: {summary['total_models_scanned']}")
        print(f"  Safety Rate: {summary['safety_percentage']:.1f}%")
        print(f"  Common Issues: {list(report['common_issues'].keys())[:3]}")
    
    print("\n✓ Model security audit example completed")


if __name__ == "__main__":
    main()