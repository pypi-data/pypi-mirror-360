#!/usr/bin/env python3
"""
Integrated Improved Detector with Confidence Calibration

Combines all improvements from error analysis and confidence calibration:
1. Enhanced language filtering and romanized detection
2. Improved switch detection
3. Advanced confidence calibration
4. Production-ready reliability scores
"""

import os
import pickle
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from .detector_improvements import ImprovedGeneralCSDetector
from .confidence_calibrator import ConfidenceCalibrator, CalibrationResult
from ..detection.general_cs_detector import GeneralCSResult


@dataclass
class IntegratedResult:
    """Enhanced result with calibrated confidence and reliability metrics."""
    detected_languages: List[str]
    original_confidence: float
    calibrated_confidence: float
    reliability_score: float
    calibration_method: str
    switch_points: List[Dict[str, Any]]
    is_code_mixed: bool
    quality_assessment: str
    confidence_features: Dict[str, float]
    method: str = "integrated_improved"
    
    def to_detection_result(self):
        """Convert to standard DetectionResult for API compatibility."""
        from ..detection.language_detector import DetectionResult
        
        # Calculate probabilities based on calibrated confidence
        if len(self.detected_languages) == 1:
            probabilities = {self.detected_languages[0]: self.calibrated_confidence}
        else:
            # Distribute calibrated confidence among languages
            base_prob = self.calibrated_confidence / len(self.detected_languages)
            probabilities = {}
            for i, lang in enumerate(self.detected_languages):
                # Give slight preference to first language
                prob = base_prob * (1.2 if i == 0 else 0.9)
                probabilities[lang] = min(1.0, prob)
        
        return DetectionResult(
            detected_languages=self.detected_languages,
            confidence=self.calibrated_confidence,
            probabilities=probabilities,
            method=self.method,
            switch_points=[sp.get('position', 0) for sp in self.switch_points],
            token_languages=self.detected_languages if self.is_code_mixed else None
        )


class IntegratedImprovedDetector:
    """Production-ready detector with all improvements integrated."""
    
    def __init__(self, 
                 performance_mode: str = "balanced",
                 detector_mode: str = "code_switching",
                 calibration_models_path: Optional[str] = None,
                 auto_train_calibration: bool = True):
        """Initialize integrated improved detector.
        
        Args:
            performance_mode: Performance mode (fast/balanced/accurate)
            detector_mode: Detector mode (code_switching/monolingual/multilingual)  
            calibration_models_path: Path to saved calibration models
            auto_train_calibration: Whether to auto-train if models not found
        """
        
        # Initialize improved detector
        self.detector = ImprovedGeneralCSDetector(
            performance_mode=performance_mode,
            detector_mode=detector_mode
        )
        
        # Initialize calibrator
        self.calibrator = ConfidenceCalibrator(self.detector)
        self.calibration_trained = False
        
        # Try to load existing calibration models
        if calibration_models_path and os.path.exists(calibration_models_path):
            try:
                self.calibrator.load_calibration_models(calibration_models_path)
                self.calibration_trained = True
                print("✓ Loaded existing calibration models")
            except Exception as e:
                print(f"⚠️ Failed to load calibration models: {e}")
        
        # Auto-train if requested and no models loaded
        if auto_train_calibration and not self.calibration_trained:
            self._auto_train_calibration()
        
        print("🚀 Integrated Improved Detector ready")
    
    def _auto_train_calibration(self):
        """Auto-train calibration on a small dataset."""
        try:
            print("🧠 Auto-training calibration models...")
            
            # Create a small training dataset
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from comprehensive_test_dataset import create_comprehensive_test_dataset
            training_cases = create_comprehensive_test_dataset()
            
            # Train on subset to avoid overfitting
            training_subset = training_cases[:50]  
            
            # Collect data and train
            self.calibrator.collect_calibration_data(training_subset)
            self.calibrator.train_calibration_models(validation_split=0.3)
            
            # Save models
            self.calibrator.save_calibration_models("auto_trained_calibration.pkl")
            self.calibration_trained = True
            
            print("✓ Auto-training completed")
            
        except Exception as e:
            print(f"⚠️ Auto-training failed: {e}")
            print("Proceeding without calibration...")
    
    def detect_language(self, text: str, 
                       user_languages: Optional[List[str]] = None) -> IntegratedResult:
        """Detect language with all improvements applied."""
        
        # Get improved detection result
        improved_result = self.detector.detect_language(text, user_languages)
        
        # Apply confidence calibration if available
        if self.calibration_trained:
            try:
                calibration_result = self.calibrator.calibrate_confidence(
                    text, improved_result.confidence, method="feature"
                )
                calibrated_conf = calibration_result.calibrated_confidence
                reliability = calibration_result.reliability_score
                cal_method = calibration_result.calibration_method
                conf_features = calibration_result.confidence_features
            except Exception as e:
                print(f"⚠️ Calibration failed: {e}")
                calibrated_conf = improved_result.confidence
                reliability = 0.5
                cal_method = "none"
                conf_features = {}
        else:
            calibrated_conf = improved_result.confidence
            reliability = 0.5
            cal_method = "uncalibrated"
            conf_features = {}
        
        # Determine quality assessment
        quality_assessment = self._assess_quality(
            improved_result, calibrated_conf, reliability
        )
        
        return IntegratedResult(
            detected_languages=improved_result.detected_languages,
            original_confidence=improved_result.confidence,
            calibrated_confidence=calibrated_conf,
            reliability_score=reliability,
            calibration_method=cal_method,
            switch_points=improved_result.switch_points,
            is_code_mixed=improved_result.is_code_mixed,
            quality_assessment=quality_assessment,
            confidence_features=conf_features
        )
    
    def _assess_quality(self, result: GeneralCSResult, 
                       calibrated_conf: float, reliability: float) -> str:
        """Assess overall quality of detection."""
        
        # Quality factors
        factors = []
        
        # Confidence factor
        if calibrated_conf >= 0.8 and reliability >= 0.8:
            factors.append("high_confidence")
        elif calibrated_conf >= 0.6 and reliability >= 0.6:
            factors.append("medium_confidence")
        else:
            factors.append("low_confidence")
        
        # Complexity factor
        if len(result.detected_languages) == 1:
            factors.append("simple")
        elif len(result.detected_languages) == 2:
            factors.append("moderate")
        else:
            factors.append("complex")
        
        # Length factor
        word_count = len(result.debug_info.get('input_text', '').split())
        if word_count >= 10:
            factors.append("sufficient_context")
        elif word_count >= 5:
            factors.append("moderate_context")
        else:
            factors.append("limited_context")
        
        # Combine into assessment
        if "high_confidence" in factors and "simple" in factors:
            return "excellent"
        elif "high_confidence" in factors or ("medium_confidence" in factors and "sufficient_context" in factors):
            return "good" 
        elif "medium_confidence" in factors:
            return "fair"
        else:
            return "uncertain"
    
    def batch_detect(self, texts: List[str], 
                    show_progress: bool = True) -> List[IntegratedResult]:
        """Detect languages for multiple texts efficiently."""
        
        results = []
        
        for i, text in enumerate(texts):
            if show_progress and (i + 1) % 25 == 0:
                print(f"Processed {i + 1}/{len(texts)} texts...")
            
            result = self.detect_language(text)
            results.append(result)
        
        if show_progress:
            print(f"✓ Batch processing complete: {len(texts)} texts")
        
        return results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of detector capabilities and performance."""
        
        return {
            "detector_info": {
                "base_detector": "ImprovedGeneralCSDetector",
                "performance_mode": self.detector.performance_mode,
                "detector_mode": self.detector.detector_mode,
                "calibration_trained": self.calibration_trained
            },
            "improvements": {
                "error_analysis_fixes": True,
                "confidence_calibration": self.calibration_trained,
                "romanized_detection": True,
                "language_filtering": True,
                "switch_detection": True
            },
            "capabilities": {
                "api_compatible": True,
                "real_time": True,
                "batch_processing": True,
                "reliability_scoring": True,
                "quality_assessment": True
            }
        }


def demo_integrated_detector():
    """Demo the integrated improved detector."""
    
    print("🚀 INTEGRATED IMPROVED DETECTOR DEMO")
    print("=" * 50)
    
    # Initialize detector
    detector = IntegratedImprovedDetector(
        performance_mode="balanced",
        auto_train_calibration=True
    )
    
    # Test cases showing improvements
    test_cases = [
        "Yallah chalein",  # Previously problematic
        "I need chai right now",  # Previously wrong language
        "Hello world",  # Should be simple and confident  
        "Hola, ¿cómo estás? I am doing bien today",  # Code-switching
        "Ok चलो",  # Mixed script
        "This is a longer English sentence that should be detected correctly with high confidence"
    ]
    
    print(f"\n📝 Testing {len(test_cases)} cases:")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. \"{text}\"")
        
        result = detector.detect_language(text)
        
        print(f"   Languages: {result.detected_languages}")
        print(f"   Confidence: {result.original_confidence:.3f} → {result.calibrated_confidence:.3f}")
        print(f"   Reliability: {result.reliability_score:.3f}")
        print(f"   Quality: {result.quality_assessment}")
        print(f"   Method: {result.calibration_method}")
        
        if result.is_code_mixed:
            print(f"   Switches: {len(result.switch_points)}")
    
    print(f"\n📊 Performance Summary:")
    summary = detector.get_performance_summary()
    for category, info in summary.items():
        print(f"  {category}:")
        for key, value in info.items():
            print(f"    {key}: {value}")
    
    return detector


if __name__ == "__main__":
    demo_integrated_detector()