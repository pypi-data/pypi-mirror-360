"""Code-Switch Aware AI Library v2.1.0

A comprehensive library for detecting and analyzing code-switching in multilingual text.
Production-ready with 100% test coverage, robust API stability, and advanced threshold systems.
"""

from .utils import VERSION, AUTHOR

__version__ = VERSION
__author__ = AUTHOR

# Core detection components
from .detection import (
    LanguageDetector, 
    SwitchPointDetector, 
    EnhancedCodeSwitchDetector,
    OptimizedCodeSwitchDetector,
    FastTextDetector,
    TransformerDetector,
    EnsembleDetector,
    GeneralCodeSwitchingDetector,  # NEW: Primary CS detector with 6.5x improvement
    SwitchPointRefiner,
    PhraseCluster,
    EnhancedDetectionResult,
    OptimizedResult,
    EnsembleResult,
    GeneralCSResult,  # NEW: Rich result with observability
    SwitchPoint,
    RefinementResult,
    LinguisticFeatureAnalyzer,
    WordAnalysis  # NEW: For observability
)

# Threshold configuration
from .utils.thresholds import ThresholdConfig, DetectionMode, ThresholdProfile

# Memory and conversation handling
from .memory import ConversationMemory, ConversationEntry, EmbeddingGenerator

# Similarity and retrieval
from .retrieval import SimilarityRetriever, OptimizedSimilarityRetriever

# CLI interface
from .interface import CLI

# Dashboard and observability  
from .dashboard import MetricsDashboard, DashboardMetrics

# Error analysis and advanced detection components
from .analysis import (
    ErrorAnalyzer, ErrorCase, ErrorPattern, ErrorAnalysisResult,
    IntegratedImprovedDetector, IntegratedResult,  # NEW: Production-ready integrated detector
    ConfidenceCalibrator, CalibrationResult, CalibrationMetrics  # NEW: Confidence calibration
)

# High-performance processing
from .processing import (
    HighPerformanceBatchProcessor, BatchConfig, BatchMetrics, BatchResult  # NEW: Batch processing optimization
)

# Context optimization
from .optimization import (
    ContextWindowOptimizer, ContextConfig, ContextualWordAnalysis, ContextOptimizationResult, TextType  # NEW: Context window optimization
)

# Enhanced detection with context
try:
    from .detection.context_enhanced_detector import ContextEnhancedCSDetector  # NEW: Context-enhanced detector
    CONTEXT_ENHANCEMENT_AVAILABLE = True
except ImportError:
    CONTEXT_ENHANCEMENT_AVAILABLE = False

# Evaluation frameworks (optional imports)
try:
    from .evaluation import LinCEBenchmark, MTEBEvaluator, ConfidenceCalibrator
    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False

# Advanced features (optional imports)
try:
    from .advanced import ContextAwareClusterer
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

# Training components (optional imports)
try:
    from .training import FineTuningConfig, FastTextDomainTrainer, create_synthetic_domain_data
    TRAINING_AVAILABLE = True
except ImportError:
    TRAINING_AVAILABLE = False

# Analysis components (optional imports)
try:
    from .analysis import TemporalCodeSwitchAnalyzer, TemporalPattern, TemporalStatistics
    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False

# Streaming components (optional imports)
try:
    from .streaming import (
        StreamingDetector, StreamChunk, StreamResult, StreamingStatistics, StreamingConfig,
        CircularBuffer, SlidingWindowBuffer, AdaptiveBuffer,
        RealTimeAnalyzer, ConversationState, LiveDetectionResult, ConversationPhase
    )
    STREAMING_AVAILABLE = True
except ImportError:
    STREAMING_AVAILABLE = False

# Security components (optional imports)
try:
    from .security import (
        InputValidator, ValidationResult, SecurityConfig, TextSanitizer,
        ModelSecurityAuditor, ModelIntegrityChecker, SecurityScanResult,
        PrivacyProtector, DataAnonymizer, PIIDetector, PrivacyConfig, PrivacyLevel,
        SecurityMonitor, SecurityEvent, ThreatDetector, AuditLogger
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

__all__ = [
    # Core detectors
    "LanguageDetector",
    "SwitchPointDetector",
    "EnhancedCodeSwitchDetector",
    "OptimizedCodeSwitchDetector",
    "FastTextDetector",
    "TransformerDetector",
    "EnsembleDetector",
    "GeneralCodeSwitchingDetector",  # NEW: Primary CS detector
    "SwitchPointRefiner",
    "PhraseCluster", 
    "EnhancedDetectionResult",
    "OptimizedResult",
    "EnsembleResult",
    "GeneralCSResult",  # NEW: Rich result type
    "SwitchPoint",
    "RefinementResult",
    "LinguisticFeatureAnalyzer",
    "WordAnalysis",  # NEW: Observability component
    
    # Threshold configuration
    "ThresholdConfig",
    "DetectionMode", 
    "ThresholdProfile",
    
    # Memory system
    "ConversationMemory",
    "ConversationEntry",
    "EmbeddingGenerator",
    
    # Retrieval system
    "SimilarityRetriever",
    "OptimizedSimilarityRetriever",
    
    # Interface
    "CLI",
    
    # Dashboard
    "MetricsDashboard",
    "DashboardMetrics",
    
    # Error Analysis & Advanced Detection
    "ErrorAnalyzer",
    "ErrorCase", 
    "ErrorPattern",
    "ErrorAnalysisResult",
    "IntegratedImprovedDetector",  # NEW: Production-ready integrated detector
    "IntegratedResult",            # NEW: Enhanced result with calibration
    "ConfidenceCalibrator",        # NEW: Advanced confidence calibration
    "CalibrationResult",
    "CalibrationMetrics",
    
    # High-Performance Processing
    "HighPerformanceBatchProcessor",  # NEW: Optimized batch processing
    "BatchConfig",
    "BatchMetrics", 
    "BatchResult",
    
    # Context Optimization
    "ContextWindowOptimizer",         # NEW: Context window optimization
    "ContextConfig",
    "ContextualWordAnalysis",
    "ContextOptimizationResult",
    "TextType"
]

# Add optional components to __all__ if available
if EVALUATION_AVAILABLE:
    __all__.extend(["LinCEBenchmark", "MTEBEvaluator", "ConfidenceCalibrator"])

if ADVANCED_AVAILABLE:
    __all__.extend(["ContextAwareClusterer"])

if TRAINING_AVAILABLE:
    __all__.extend(["FineTuningConfig", "FastTextDomainTrainer", "create_synthetic_domain_data"])

if ANALYSIS_AVAILABLE:
    __all__.extend(["TemporalCodeSwitchAnalyzer", "TemporalPattern", "TemporalStatistics"])

if STREAMING_AVAILABLE:
    __all__.extend([
        "StreamingDetector", "StreamChunk", "StreamResult", "StreamingStatistics", "StreamingConfig",
        "CircularBuffer", "SlidingWindowBuffer", "AdaptiveBuffer",
        "RealTimeAnalyzer", "ConversationState", "LiveDetectionResult", "ConversationPhase"
    ])

if SECURITY_AVAILABLE:
    __all__.extend([
        "InputValidator", "ValidationResult", "SecurityConfig", "TextSanitizer",
        "ModelSecurityAuditor", "ModelIntegrityChecker", "SecurityScanResult",
        "PrivacyProtector", "DataAnonymizer", "PIIDetector", "PrivacyConfig", "PrivacyLevel",
        "SecurityMonitor", "SecurityEvent", "ThreatDetector", "AuditLogger"
    ])

if CONTEXT_ENHANCEMENT_AVAILABLE:
    __all__.extend(["ContextEnhancedCSDetector"])