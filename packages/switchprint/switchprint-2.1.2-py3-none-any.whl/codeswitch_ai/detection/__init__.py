"""Language detection and code-switch point identification."""

from .language_detector import LanguageDetector
from .switch_detector import SwitchPointDetector
from .enhanced_detector import EnhancedCodeSwitchDetector, PhraseCluster, EnhancedDetectionResult
from .optimized_detector import OptimizedCodeSwitchDetector, OptimizedResult
from .fasttext_detector import FastTextDetector
from .transformer_detector import TransformerDetector
from .ensemble_detector import EnsembleDetector, EnsembleResult
from .general_cs_detector import GeneralCodeSwitchingDetector, GeneralCSResult, WordAnalysis
from .switch_point_refiner import SwitchPointRefiner, SwitchPoint, RefinementResult, LinguisticFeatureAnalyzer

# Zero-shot detection (optional)
try:
    from .zero_shot_detector import ZeroShotLanguageDetector, ZeroShotResult
    ZERO_SHOT_AVAILABLE = True
except ImportError:
    ZERO_SHOT_AVAILABLE = False

__all__ = [
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
    "WordAnalysis"  # NEW: Observability component
]

# Add zero-shot components if available
if ZERO_SHOT_AVAILABLE:
    __all__.extend(["ZeroShotLanguageDetector", "ZeroShotResult"])