#!/usr/bin/env python3
"""Security monitoring and threat detection for code-switching AI systems."""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import threading
import hashlib
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events."""
    INPUT_VALIDATION_FAILURE = "input_validation_failure"
    PII_DETECTION = "pii_detection"
    MODEL_INTEGRITY_VIOLATION = "model_integrity_violation"
    SUSPICIOUS_ACCESS_PATTERN = "suspicious_access_pattern"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION_ATTEMPT = "data_exfiltration_attempt"
    INJECTION_ATTEMPT = "injection_attempt"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    PRIVACY_VIOLATION = "privacy_violation"


class SecuritySeverity(Enum):
    """Security event severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event data structure."""
    event_type: SecurityEventType
    severity: SecuritySeverity
    timestamp: float
    source_id: str
    description: str
    metadata: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['severity'] = self.severity.value
        return result
    
    def get_event_hash(self) -> str:
        """Generate unique hash for this event."""
        event_str = f"{self.event_type.value}{self.timestamp}{self.source_id}{self.description}"
        return hashlib.md5(event_str.encode()).hexdigest()[:16]


class ThreatDetector:
    """Detect security threats based on patterns and anomalies."""
    
    def __init__(self):
        """Initialize threat detector."""
        # Rate limiting tracking
        self.access_patterns = defaultdict(lambda: deque(maxlen=100))
        self.rate_limits = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'failed_attempts_per_minute': 10
        }
        
        # Suspicious pattern detection
        self.failed_attempts = defaultdict(list)
        self.suspicious_ips = set()
        
        # Behavioral baselines
        self.user_baselines = defaultdict(lambda: {
            'average_request_size': 0,
            'common_languages': set(),
            'typical_request_times': [],
            'request_count': 0
        })
        
        # Anomaly detection thresholds
        self.anomaly_thresholds = {
            'request_size_multiplier': 5.0,  # 5x larger than normal
            'unusual_language_threshold': 0.8,  # 80% confidence for unusual language
            'time_anomaly_threshold': 2.0,  # 2 standard deviations
            'burst_threshold': 10  # 10 requests in 1 minute
        }
    
    def detect_rate_limit_violation(self, source_id: str, user_id: Optional[str] = None) -> Optional[SecurityEvent]:
        """Detect rate limit violations.
        
        Args:
            source_id: Source identifier
            user_id: Optional user identifier
            
        Returns:
            Security event if violation detected
        """
        current_time = time.time()
        identifier = user_id or source_id
        
        # Add current request
        self.access_patterns[identifier].append(current_time)
        
        # Check rate limits
        recent_requests = [
            timestamp for timestamp in self.access_patterns[identifier]
            if current_time - timestamp <= 60  # Last minute
        ]
        
        if len(recent_requests) > self.rate_limits['requests_per_minute']:
            return SecurityEvent(
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                severity=SecuritySeverity.MEDIUM,
                timestamp=current_time,
                source_id=source_id,
                description=f"Rate limit exceeded: {len(recent_requests)} requests in last minute",
                metadata={
                    'request_count': len(recent_requests),
                    'time_window': 60,
                    'limit': self.rate_limits['requests_per_minute']
                },
                user_id=user_id
            )
        
        # Check hourly limits
        hourly_requests = [
            timestamp for timestamp in self.access_patterns[identifier]
            if current_time - timestamp <= 3600  # Last hour
        ]
        
        if len(hourly_requests) > self.rate_limits['requests_per_hour']:
            return SecurityEvent(
                event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                severity=SecuritySeverity.HIGH,
                timestamp=current_time,
                source_id=source_id,
                description=f"Hourly rate limit exceeded: {len(hourly_requests)} requests",
                metadata={
                    'request_count': len(hourly_requests),
                    'time_window': 3600,
                    'limit': self.rate_limits['requests_per_hour']
                },
                user_id=user_id
            )
        
        return None
    
    def detect_suspicious_access_pattern(self, source_id: str, 
                                       user_id: Optional[str] = None,
                                       ip_address: Optional[str] = None,
                                       success: bool = True) -> Optional[SecurityEvent]:
        """Detect suspicious access patterns.
        
        Args:
            source_id: Source identifier
            user_id: Optional user identifier
            ip_address: Optional IP address
            success: Whether the request was successful
            
        Returns:
            Security event if suspicious pattern detected
        """
        current_time = time.time()
        identifier = user_id or source_id
        
        if not success:
            # Track failed attempts
            self.failed_attempts[identifier].append(current_time)
            
            # Clean old attempts (older than 1 hour)
            cutoff_time = current_time - 3600
            self.failed_attempts[identifier] = [
                timestamp for timestamp in self.failed_attempts[identifier]
                if timestamp > cutoff_time
            ]
            
            # Check for excessive failed attempts
            recent_failures = [
                timestamp for timestamp in self.failed_attempts[identifier]
                if current_time - timestamp <= 60  # Last minute
            ]
            
            if len(recent_failures) > self.rate_limits['failed_attempts_per_minute']:
                # Mark IP as suspicious if provided
                if ip_address:
                    self.suspicious_ips.add(ip_address)
                
                return SecurityEvent(
                    event_type=SecurityEventType.SUSPICIOUS_ACCESS_PATTERN,
                    severity=SecuritySeverity.HIGH,
                    timestamp=current_time,
                    source_id=source_id,
                    description=f"Excessive failed attempts: {len(recent_failures)} in last minute",
                    metadata={
                        'failed_attempts': len(recent_failures),
                        'total_failures': len(self.failed_attempts[identifier]),
                        'suspicious_ip': ip_address in self.suspicious_ips if ip_address else False
                    },
                    user_id=user_id,
                    ip_address=ip_address
                )
        
        # Check for access from known suspicious IPs
        if ip_address and ip_address in self.suspicious_ips:
            return SecurityEvent(
                event_type=SecurityEventType.SUSPICIOUS_ACCESS_PATTERN,
                severity=SecuritySeverity.MEDIUM,
                timestamp=current_time,
                source_id=source_id,
                description=f"Access from suspicious IP: {ip_address}",
                metadata={'suspicious_ip': ip_address},
                user_id=user_id,
                ip_address=ip_address
            )
        
        return None
    
    def detect_behavioral_anomaly(self, user_id: str, 
                                request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect behavioral anomalies for a user.
        
        Args:
            user_id: User identifier
            request_data: Request data including text size, languages, etc.
            
        Returns:
            Security event if anomaly detected
        """
        current_time = time.time()
        baseline = self.user_baselines[user_id]
        
        # Update baseline data
        baseline['request_count'] += 1
        baseline['typical_request_times'].append(current_time)
        
        # Keep only recent times (last 100 requests)
        baseline['typical_request_times'] = baseline['typical_request_times'][-100:]
        
        # Check request size anomaly
        text_size = request_data.get('text_size', 0)
        if text_size > 0:
            # Update average request size
            if baseline['average_request_size'] == 0:
                baseline['average_request_size'] = text_size
            else:
                baseline['average_request_size'] = (
                    baseline['average_request_size'] * 0.9 + text_size * 0.1
                )
            
            # Check for unusually large requests
            size_threshold = baseline['average_request_size'] * self.anomaly_thresholds['request_size_multiplier']
            if text_size > size_threshold and baseline['request_count'] > 10:
                return SecurityEvent(
                    event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                    severity=SecuritySeverity.MEDIUM,
                    timestamp=current_time,
                    source_id=user_id,
                    description=f"Unusually large request: {text_size} bytes (avg: {baseline['average_request_size']:.1f})",
                    metadata={
                        'request_size': text_size,
                        'average_size': baseline['average_request_size'],
                        'threshold_multiplier': self.anomaly_thresholds['request_size_multiplier']
                    },
                    user_id=user_id
                )
        
        # Check language usage anomaly
        detected_languages = request_data.get('detected_languages', [])
        if detected_languages:
            baseline['common_languages'].update(detected_languages)
            
            # Check for unusual languages (if user has established pattern)
            if baseline['request_count'] > 20:
                unusual_languages = set(detected_languages) - baseline['common_languages']
                if unusual_languages:
                    return SecurityEvent(
                        event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                        severity=SecuritySeverity.LOW,
                        timestamp=current_time,
                        source_id=user_id,
                        description=f"Unusual languages detected: {list(unusual_languages)}",
                        metadata={
                            'unusual_languages': list(unusual_languages),
                            'common_languages': list(baseline['common_languages']),
                            'detected_languages': detected_languages
                        },
                        user_id=user_id
                    )
        
        # Check for burst activity
        recent_times = [
            t for t in baseline['typical_request_times']
            if current_time - t <= 60  # Last minute
        ]
        
        if len(recent_times) > self.anomaly_thresholds['burst_threshold']:
            return SecurityEvent(
                event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                severity=SecuritySeverity.MEDIUM,
                timestamp=current_time,
                source_id=user_id,
                description=f"Burst activity detected: {len(recent_times)} requests in last minute",
                metadata={
                    'burst_size': len(recent_times),
                    'threshold': self.anomaly_thresholds['burst_threshold'],
                    'time_window': 60
                },
                user_id=user_id
            )
        
        return None
    
    def update_threat_intelligence(self, suspicious_ips: List[str], 
                                 threat_indicators: Dict[str, Any]) -> None:
        """Update threat intelligence data.
        
        Args:
            suspicious_ips: List of suspicious IP addresses
            threat_indicators: Additional threat indicators
        """
        self.suspicious_ips.update(suspicious_ips)
        
        # Update thresholds based on threat intelligence
        if 'rate_limits' in threat_indicators:
            self.rate_limits.update(threat_indicators['rate_limits'])
        
        if 'anomaly_thresholds' in threat_indicators:
            self.anomaly_thresholds.update(threat_indicators['anomaly_thresholds'])
        
        logger.info(f"Updated threat intelligence: {len(suspicious_ips)} IPs, "
                   f"{len(threat_indicators)} indicators")


class AuditLogger:
    """Audit logging for security events."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize audit logger.
        
        Args:
            log_file: Optional path to audit log file
        """
        self.log_file = log_file
        self.in_memory_log = deque(maxlen=1000)  # Keep last 1000 events in memory
        
        # File logging setup
        if self.log_file:
            self.file_logger = logging.getLogger('security_audit')
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.file_logger.addHandler(handler)
            self.file_logger.setLevel(logging.INFO)
    
    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event.
        
        Args:
            event: Security event to log
        """
        # Add to in-memory log
        self.in_memory_log.append(event)
        
        # Log to file if configured
        if self.log_file and hasattr(self, 'file_logger'):
            log_message = json.dumps(event.to_dict())
            
            if event.severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]:
                self.file_logger.error(log_message)
            elif event.severity == SecuritySeverity.MEDIUM:
                self.file_logger.warning(log_message)
            else:
                self.file_logger.info(log_message)
        
        # Console logging for high severity events
        if event.severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]:
            logger.error(f"Security Event: {event.description}")
        elif event.severity == SecuritySeverity.MEDIUM:
            logger.warning(f"Security Event: {event.description}")
    
    def get_recent_events(self, count: int = 100, 
                         severity_filter: Optional[SecuritySeverity] = None) -> List[SecurityEvent]:
        """Get recent security events.
        
        Args:
            count: Number of events to return
            severity_filter: Optional severity filter
            
        Returns:
            List of recent security events
        """
        events = list(self.in_memory_log)
        
        if severity_filter:
            events = [event for event in events if event.severity == severity_filter]
        
        return events[-count:]
    
    def generate_audit_report(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate audit report for specified time range.
        
        Args:
            time_range_hours: Time range in hours
            
        Returns:
            Audit report dictionary
        """
        cutoff_time = time.time() - (time_range_hours * 3600)
        recent_events = [
            event for event in self.in_memory_log
            if event.timestamp > cutoff_time
        ]
        
        if not recent_events:
            return {
                'summary': 'No security events in specified time range',
                'time_range_hours': time_range_hours,
                'event_count': 0
            }
        
        # Event type distribution
        event_type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        user_events = defaultdict(int)
        
        for event in recent_events:
            event_type_counts[event.event_type.value] += 1
            severity_counts[event.severity.value] += 1
            if event.user_id:
                user_events[event.user_id] += 1
        
        # Top security issues
        top_event_types = sorted(
            event_type_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Users with most events
        top_users = sorted(
            user_events.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        report = {
            'summary': {
                'time_range_hours': time_range_hours,
                'total_events': len(recent_events),
                'unique_users': len(user_events),
                'high_severity_events': severity_counts.get('high', 0) + severity_counts.get('critical', 0)
            },
            'event_distribution': {
                'by_type': dict(event_type_counts),
                'by_severity': dict(severity_counts)
            },
            'top_issues': top_event_types,
            'top_users_by_events': top_users,
            'recent_critical_events': [
                event.to_dict() for event in recent_events[-10:]
                if event.severity == SecuritySeverity.CRITICAL
            ],
            'timestamp': time.time()
        }
        
        return report


class SecurityMonitor:
    """Main security monitoring orchestrator."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize security monitor.
        
        Args:
            log_file: Optional path to audit log file
        """
        self.threat_detector = ThreatDetector()
        self.audit_logger = AuditLogger(log_file)
        
        # Event handlers
        self.event_handlers = defaultdict(list)
        
        # Monitoring statistics
        self.monitoring_stats = {
            'start_time': time.time(),
            'events_processed': 0,
            'threats_detected': 0,
            'active_sessions': set()
        }
        
        logger.info("Security monitor initialized")
    
    def register_event_handler(self, event_type: SecurityEventType, 
                             handler: Callable[[SecurityEvent], None]) -> None:
        """Register handler for specific event types.
        
        Args:
            event_type: Type of security event
            handler: Handler function
        """
        self.event_handlers[event_type].append(handler)
    
    def process_request(self, source_id: str, 
                       request_data: Dict[str, Any],
                       user_id: Optional[str] = None,
                       ip_address: Optional[str] = None,
                       success: bool = True) -> List[SecurityEvent]:
        """Process a request and detect security events.
        
        Args:
            source_id: Source identifier
            request_data: Request data
            user_id: Optional user identifier
            ip_address: Optional IP address
            success: Whether request was successful
            
        Returns:
            List of detected security events
        """
        events = []
        
        # Track session
        if user_id:
            self.monitoring_stats['active_sessions'].add(user_id)
        
        # Rate limit detection
        rate_event = self.threat_detector.detect_rate_limit_violation(source_id, user_id)
        if rate_event:
            events.append(rate_event)
        
        # Suspicious access pattern detection
        access_event = self.threat_detector.detect_suspicious_access_pattern(
            source_id, user_id, ip_address, success
        )
        if access_event:
            events.append(access_event)
        
        # Behavioral anomaly detection (only for successful requests with user ID)
        if success and user_id:
            anomaly_event = self.threat_detector.detect_behavioral_anomaly(user_id, request_data)
            if anomaly_event:
                events.append(anomaly_event)
        
        # Process detected events
        for event in events:
            self._handle_security_event(event)
        
        self.monitoring_stats['events_processed'] += 1
        if events:
            self.monitoring_stats['threats_detected'] += len(events)
        
        return events
    
    def log_security_event(self, event_type: SecurityEventType,
                          severity: SecuritySeverity,
                          description: str,
                          source_id: str,
                          metadata: Optional[Dict[str, Any]] = None,
                          user_id: Optional[str] = None) -> SecurityEvent:
        """Manually log a security event.
        
        Args:
            event_type: Type of security event
            severity: Event severity
            description: Event description
            source_id: Source identifier
            metadata: Optional event metadata
            user_id: Optional user identifier
            
        Returns:
            Created security event
        """
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            timestamp=time.time(),
            source_id=source_id,
            description=description,
            metadata=metadata or {},
            user_id=user_id
        )
        
        self._handle_security_event(event)
        return event
    
    def _handle_security_event(self, event: SecurityEvent) -> None:
        """Handle a security event.
        
        Args:
            event: Security event to handle
        """
        # Log the event
        self.audit_logger.log_event(event)
        
        # Call registered handlers
        for handler in self.event_handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in security event handler: {e}")
        
        # Auto-response for critical events
        if event.severity == SecuritySeverity.CRITICAL:
            self._handle_critical_event(event)
    
    def _handle_critical_event(self, event: SecurityEvent) -> None:
        """Handle critical security events with automatic response.
        
        Args:
            event: Critical security event
        """
        logger.critical(f"CRITICAL SECURITY EVENT: {event.description}")
        
        # Additional critical event handling could include:
        # - Alerting administrators
        # - Temporarily blocking IPs/users
        # - Triggering incident response procedures
        
        # For now, just log the critical event
        critical_log = {
            'timestamp': event.timestamp,
            'event_hash': event.get_event_hash(),
            'description': event.description,
            'source': event.source_id,
            'user': event.user_id,
            'ip': event.ip_address
        }
        
        logger.critical(f"Critical event details: {json.dumps(critical_log)}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status.
        
        Returns:
            Monitoring status dictionary
        """
        current_time = time.time()
        uptime = current_time - self.monitoring_stats['start_time']
        
        return {
            'uptime_seconds': uptime,
            'events_processed': self.monitoring_stats['events_processed'],
            'threats_detected': self.monitoring_stats['threats_detected'],
            'active_sessions': len(self.monitoring_stats['active_sessions']),
            'threat_detection_rate': (
                self.monitoring_stats['threats_detected'] / 
                max(self.monitoring_stats['events_processed'], 1)
            ),
            'suspicious_ips': len(self.threat_detector.suspicious_ips),
            'timestamp': current_time
        }
    
    def generate_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive security report.
        
        Args:
            hours: Time range in hours
            
        Returns:
            Security report
        """
        audit_report = self.audit_logger.generate_audit_report(hours)
        monitoring_status = self.get_monitoring_status()
        
        combined_report = {
            'monitoring_status': monitoring_status,
            'audit_summary': audit_report,
            'threat_intelligence': {
                'suspicious_ips': list(self.threat_detector.suspicious_ips),
                'rate_limits': self.threat_detector.rate_limits,
                'anomaly_thresholds': self.threat_detector.anomaly_thresholds
            },
            'report_timestamp': time.time()
        }
        
        return combined_report


def main():
    """Example usage of security monitoring."""
    print("🔒 Security Monitoring Example")
    print("=" * 40)
    
    # Initialize security monitor
    monitor = SecurityMonitor()
    
    # Register event handler for demonstration
    def alert_handler(event: SecurityEvent):
        if event.severity in [SecuritySeverity.HIGH, SecuritySeverity.CRITICAL]:
            print(f"🚨 ALERT: {event.description}")
    
    monitor.register_event_handler(SecurityEventType.RATE_LIMIT_EXCEEDED, alert_handler)
    monitor.register_event_handler(SecurityEventType.SUSPICIOUS_ACCESS_PATTERN, alert_handler)
    
    # Simulate various requests
    print("\n🔄 Simulating security events:")
    
    # Normal requests
    for i in range(5):
        events = monitor.process_request(
            source_id=f"api_request_{i}",
            request_data={'text_size': 100, 'detected_languages': ['english']},
            user_id="user_123",
            ip_address="192.168.1.100",
            success=True
        )
        if events:
            print(f"  Request {i}: {len(events)} security events")
    
    # Simulate rate limiting
    print("\n🔥 Simulating rate limit violation:")
    for i in range(15):  # Exceed rate limit
        events = monitor.process_request(
            source_id=f"burst_request_{i}",
            request_data={'text_size': 50},
            user_id="user_456",
            success=True
        )
    
    # Simulate failed attempts
    print("\n🚫 Simulating failed attempts:")
    for i in range(12):  # Exceed failed attempt limit
        events = monitor.process_request(
            source_id=f"failed_request_{i}",
            request_data={'text_size': 50},
            user_id="user_789",
            ip_address="10.0.0.100",
            success=False
        )
    
    # Simulate behavioral anomaly
    print("\n📊 Simulating behavioral anomaly:")
    events = monitor.process_request(
        source_id="anomaly_request",
        request_data={'text_size': 10000, 'detected_languages': ['english']},  # Large request
        user_id="user_123",  # Same user as before
        success=True
    )
    
    # Manual security event
    print("\n⚠️ Logging manual security event:")
    manual_event = monitor.log_security_event(
        event_type=SecurityEventType.PII_DETECTION,
        severity=SecuritySeverity.HIGH,
        description="PII detected in user input",
        source_id="manual_log",
        metadata={'pii_types': ['email', 'phone']},
        user_id="user_999"
    )
    
    # Generate security report
    print("\n📊 Security Report:")
    report = monitor.generate_security_report(hours=1)
    
    status = report['monitoring_status']
    audit = report['audit_summary']
    
    print(f"  Uptime: {status['uptime_seconds']:.1f}s")
    print(f"  Events Processed: {status['events_processed']}")
    print(f"  Threats Detected: {status['threats_detected']}")
    print(f"  Threat Rate: {status['threat_detection_rate']:.3f}")
    
    if 'summary' in audit:
        print(f"  Security Events (1h): {audit['summary']['total_events']}")
        print(f"  High Severity: {audit['summary']['high_severity_events']}")
    
    print("\n✓ Security monitoring example completed")


if __name__ == "__main__":
    main()