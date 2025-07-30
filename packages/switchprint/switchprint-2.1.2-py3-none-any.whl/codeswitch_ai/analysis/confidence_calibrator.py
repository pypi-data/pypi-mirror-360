#!/usr/bin/env python3
"""
Advanced Confidence Calibration for Code-Switching Detection

Addresses the critical issue where high-confidence predictions (80-100%) 
only achieve 27% accuracy. Implements multiple calibration techniques:

1. Isotonic Regression Calibration
2. Platt Scaling (Sigmoid Calibration)  
3. Temperature Scaling
4. Feature-based Calibration
5. Ensemble Calibration
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
import pickle
import json

from ..detection.general_cs_detector import GeneralCodeSwitchingDetector, GeneralCSResult


@dataclass
class CalibrationMetrics:
    """Metrics for evaluating calibration quality."""
    expected_calibration_error: float
    brier_score: float
    log_likelihood: float
    reliability_diagram: Dict[str, Any]
    confidence_histogram: Dict[str, int]
    accuracy_by_confidence: Dict[str, float]


@dataclass
class CalibrationResult:
    """Result of confidence calibration."""
    original_confidence: float
    calibrated_confidence: float
    calibration_method: str
    confidence_features: Dict[str, float]
    reliability_score: float


class ConfidenceCalibrator:
    """Advanced confidence calibration for code-switching detection."""
    
    def __init__(self, detector: Optional[GeneralCodeSwitchingDetector] = None):
        """Initialize confidence calibrator."""
        self.detector = detector or GeneralCodeSwitchingDetector(performance_mode="balanced")
        
        # Calibration models
        self.isotonic_model = None
        self.platt_model = None
        self.temperature = 1.0
        self.feature_calibrator = None
        
        # Calibration training data
        self.training_confidences = []
        self.training_accuracies = []
        self.training_features = []
        
        # Calibration parameters
        self.calibration_bins = 10
        self.min_samples_per_bin = 5
        
        print("🎯 Confidence Calibrator initialized")
    
    def collect_calibration_data(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect data for training calibration models."""
        
        print(f"📊 Collecting calibration data from {len(test_cases)} cases...")
        
        confidences = []
        accuracies = []
        features = []
        results = []
        
        for i, test_case in enumerate(test_cases):
            if (i + 1) % 25 == 0:
                print(f"  Processed {i + 1}/{len(test_cases)} cases...")
            
            text = test_case['text']
            expected_languages = set(test_case['expected_languages'])
            
            # Get detection result
            result = self.detector.detect_language(text)
            predicted_languages = set(result.detected_languages)
            
            # Determine accuracy (1.0 if correct, 0.0 if wrong)
            is_correct = 1.0 if expected_languages == predicted_languages else 0.0
            
            # Extract confidence features
            conf_features = self._extract_confidence_features(text, result)
            
            confidences.append(result.confidence)
            accuracies.append(is_correct)
            features.append(conf_features)
            results.append({
                'text': text,
                'expected': list(expected_languages),
                'predicted': list(predicted_languages),
                'confidence': result.confidence,
                'accuracy': is_correct,
                'features': conf_features
            })
        
        # Store for training
        self.training_confidences = confidences
        self.training_accuracies = accuracies
        self.training_features = features
        
        print(f"✓ Collected {len(confidences)} calibration samples")
        print(f"  Overall accuracy: {np.mean(accuracies):.1%}")
        print(f"  Average confidence: {np.mean(confidences):.3f}")
        
        return {
            'confidences': confidences,
            'accuracies': accuracies,
            'features': features,
            'results': results
        }
    
    def _extract_confidence_features(self, text: str, result: GeneralCSResult) -> Dict[str, float]:
        """Extract features that correlate with prediction reliability."""
        
        words = text.split()
        
        features = {
            # Text characteristics
            'text_length': len(text),
            'word_count': len(words),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            
            # Language detection features
            'language_count': len(result.detected_languages),
            'switch_count': len(result.switch_points),
            'is_code_mixed': float(result.is_code_mixed),
            
            # Confidence-related features
            'confidence_raw': result.confidence,
            'max_prob': max(result.probabilities.values()) if result.probabilities else 0,
            'prob_spread': max(result.probabilities.values()) - min(result.probabilities.values()) if len(result.probabilities) > 1 else 1.0,
            
            # Word analysis features
            'analyzed_words': len(result.word_analyses),
            'avg_word_confidence': np.mean([wa.final_confidence for wa in result.word_analyses]) if result.word_analyses else 0,
            'confident_words_ratio': sum(1 for wa in result.word_analyses if wa.final_confidence > 0.7) / len(result.word_analyses) if result.word_analyses else 0,
            
            # Quality metrics
            'quality_score': result.quality_metrics.get('quality_score', 0) if hasattr(result, 'quality_metrics') and result.quality_metrics else 0,
            
            # Text complexity features
            'has_punctuation': float(bool([c for c in text if c in '.,!?;:'])),
            'has_numbers': float(bool([c for c in text if c.isdigit()])),
            'has_special_chars': float(bool([c for c in text if not c.isalnum() and not c.isspace()])),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        }
        
        return features
    
    def train_calibration_models(self, validation_split: float = 0.2) -> Dict[str, Any]:
        """Train multiple calibration models."""
        
        if not self.training_confidences:
            raise ValueError("No calibration data collected. Call collect_calibration_data() first.")
        
        print("🧠 Training calibration models...")
        
        # Split data
        n_samples = len(self.training_confidences)
        n_train = int(n_samples * (1 - validation_split))
        
        # Training data
        train_conf = np.array(self.training_confidences[:n_train])
        train_acc = np.array(self.training_accuracies[:n_train])
        train_features = np.array([list(f.values()) for f in self.training_features[:n_train]])
        
        # Validation data
        val_conf = np.array(self.training_confidences[n_train:])
        val_acc = np.array(self.training_accuracies[n_train:])
        val_features = np.array([list(f.values()) for f in self.training_features[n_train:]])
        
        print(f"  Training samples: {len(train_conf)}")
        print(f"  Validation samples: {len(val_conf)}")
        
        # 1. Isotonic Regression Calibration
        print("  Training Isotonic Regression...")
        self.isotonic_model = IsotonicRegression(out_of_bounds='clip')
        self.isotonic_model.fit(train_conf, train_acc)
        
        # 2. Platt Scaling (Logistic Regression)
        print("  Training Platt Scaling...")
        self.platt_model = LogisticRegression(random_state=42)
        self.platt_model.fit(train_conf.reshape(-1, 1), train_acc)
        
        # 3. Temperature Scaling
        print("  Training Temperature Scaling...")
        self.temperature = self._find_optimal_temperature(train_conf, train_acc)
        
        # 4. Feature-based Calibration
        print("  Training Feature-based Calibration...")
        self.feature_calibrator = LogisticRegression(random_state=42, max_iter=1000)
        self.feature_calibrator.fit(train_features, train_acc)
        
        # Evaluate on validation set
        results = {}
        
        if len(val_conf) > 0:
            print("  Evaluating calibration methods...")
            
            # Original (uncalibrated)
            original_ece = self._calculate_expected_calibration_error(val_conf, val_acc)
            results['original'] = {'ece': original_ece, 'brier': brier_score_loss(val_acc, val_conf)}
            
            # Isotonic
            iso_cal = self.isotonic_model.predict(val_conf)
            iso_ece = self._calculate_expected_calibration_error(iso_cal, val_acc)
            results['isotonic'] = {'ece': iso_ece, 'brier': brier_score_loss(val_acc, iso_cal)}
            
            # Platt
            platt_cal = self.platt_model.predict_proba(val_conf.reshape(-1, 1))[:, 1]
            platt_ece = self._calculate_expected_calibration_error(platt_cal, val_acc)
            results['platt'] = {'ece': platt_ece, 'brier': brier_score_loss(val_acc, platt_cal)}
            
            # Temperature
            temp_cal = self._apply_temperature_scaling(val_conf)
            temp_ece = self._calculate_expected_calibration_error(temp_cal, val_acc)
            results['temperature'] = {'ece': temp_ece, 'brier': brier_score_loss(val_acc, temp_cal)}
            
            # Feature-based
            feat_cal = self.feature_calibrator.predict_proba(val_features)[:, 1]
            feat_ece = self._calculate_expected_calibration_error(feat_cal, val_acc)
            results['feature'] = {'ece': feat_ece, 'brier': brier_score_loss(val_acc, feat_cal)}
            
            # Print results
            print("\n📊 Calibration Results:")
            for method, metrics in results.items():
                print(f"  {method:12}: ECE={metrics['ece']:.3f}, Brier={metrics['brier']:.3f}")
        
        print("✓ Calibration models trained successfully")
        return results
    
    def _find_optimal_temperature(self, confidences: np.ndarray, accuracies: np.ndarray) -> float:
        """Find optimal temperature for temperature scaling."""
        
        def temperature_loss(temp):
            scaled_conf = self._apply_temperature_scaling(confidences, temp)
            return self._calculate_expected_calibration_error(scaled_conf, accuracies)
        
        # Search for optimal temperature
        best_temp = 1.0
        best_loss = float('inf')
        
        for temp in np.linspace(0.1, 3.0, 30):
            loss = temperature_loss(temp)
            if loss < best_loss:
                best_loss = loss
                best_temp = temp
        
        return best_temp
    
    def _apply_temperature_scaling(self, confidences: np.ndarray, temperature: Optional[float] = None) -> np.ndarray:
        """Apply temperature scaling to confidences."""
        temp = temperature if temperature is not None else self.temperature
        
        # Convert to logits, scale, then back to probabilities
        epsilon = 1e-7
        confidences = np.clip(confidences, epsilon, 1 - epsilon)
        logits = np.log(confidences / (1 - confidences))
        scaled_logits = logits / temp
        scaled_conf = 1 / (1 + np.exp(-scaled_logits))
        
        return scaled_conf
    
    def _calculate_expected_calibration_error(self, confidences: np.ndarray, 
                                           accuracies: np.ndarray, 
                                           n_bins: int = 10) -> float:
        """Calculate Expected Calibration Error (ECE)."""
        
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find samples in this bin
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = accuracies[in_bin].mean()
                avg_confidence_in_bin = confidences[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    def calibrate_confidence(self, text: str, original_confidence: float, 
                           method: str = "best") -> CalibrationResult:
        """Calibrate confidence for a single prediction."""
        
        if not self.isotonic_model:
            raise ValueError("Calibration models not trained. Call train_calibration_models() first.")
        
        # Get detection result for feature extraction
        result = self.detector.detect_language(text)
        features = self._extract_confidence_features(text, result)
        feature_array = np.array(list(features.values())).reshape(1, -1)
        
        # Apply different calibration methods
        calibrated_confidences = {
            'isotonic': self.isotonic_model.predict([original_confidence])[0],
            'platt': self.platt_model.predict_proba([[original_confidence]])[0, 1],
            'temperature': self._apply_temperature_scaling(np.array([original_confidence]))[0],
            'feature': self.feature_calibrator.predict_proba(feature_array)[0, 1]
        }
        
        # Choose best method or specific method
        if method == "best":
            # Use feature-based as default "best" method
            calibrated_conf = calibrated_confidences['feature']
            used_method = "feature"
        elif method in calibrated_confidences:
            calibrated_conf = calibrated_confidences[method]
            used_method = method
        else:
            calibrated_conf = original_confidence
            used_method = "none"
        
        # Calculate reliability score
        reliability = self._calculate_reliability_score(features, calibrated_conf)
        
        return CalibrationResult(
            original_confidence=original_confidence,
            calibrated_confidence=calibrated_conf,
            calibration_method=used_method,
            confidence_features=features,
            reliability_score=reliability
        )
    
    def _calculate_reliability_score(self, features: Dict[str, float], 
                                   calibrated_confidence: float) -> float:
        """Calculate reliability score for calibrated confidence."""
        
        # Factors that increase reliability
        reliability_factors = []
        
        # Text length factor
        word_count = features.get('word_count', 0)
        if word_count >= 5:
            reliability_factors.append(0.8)
        elif word_count >= 3:
            reliability_factors.append(0.6)
        else:
            reliability_factors.append(0.4)
        
        # Language clarity factor
        if features.get('language_count', 1) == 1:
            reliability_factors.append(0.9)  # Monolingual more reliable
        elif features.get('language_count', 1) == 2:
            reliability_factors.append(0.7)  # Simple CS
        else:
            reliability_factors.append(0.5)  # Complex multilingual
        
        # Confidence consistency factor
        prob_spread = features.get('prob_spread', 0)
        if prob_spread > 0.5:
            reliability_factors.append(0.8)  # Clear winner
        elif prob_spread > 0.3:
            reliability_factors.append(0.6)  # Moderate confidence
        else:
            reliability_factors.append(0.4)  # Close call
        
        # Word analysis consistency
        confident_words_ratio = features.get('confident_words_ratio', 0)
        reliability_factors.append(confident_words_ratio * 0.8 + 0.2)
        
        # Combine factors
        base_reliability = np.mean(reliability_factors)
        
        # Adjust based on calibrated confidence
        if 0.7 <= calibrated_confidence <= 0.9:
            confidence_factor = 1.0  # Sweet spot
        elif calibrated_confidence > 0.9:
            confidence_factor = 0.9  # Too confident
        elif calibrated_confidence < 0.5:
            confidence_factor = 0.7  # Low confidence
        else:
            confidence_factor = 0.85  # Moderate confidence
        
        return base_reliability * confidence_factor
    
    def evaluate_calibration(self, test_cases: List[Dict[str, Any]], 
                           method: str = "feature") -> CalibrationMetrics:
        """Evaluate calibration quality on test cases."""
        
        print(f"📈 Evaluating calibration using {method} method...")
        
        original_confidences = []
        calibrated_confidences = []
        accuracies = []
        
        for test_case in test_cases:
            text = test_case['text']
            expected_languages = set(test_case['expected_languages'])
            
            # Get original prediction
            result = self.detector.detect_language(text)
            predicted_languages = set(result.detected_languages)
            
            # Calibrate confidence
            cal_result = self.calibrate_confidence(text, result.confidence, method)
            
            # Record data
            original_confidences.append(result.confidence)
            calibrated_confidences.append(cal_result.calibrated_confidence)
            accuracies.append(1.0 if expected_languages == predicted_languages else 0.0)
        
        # Calculate metrics
        orig_conf = np.array(original_confidences)
        cal_conf = np.array(calibrated_confidences)
        acc = np.array(accuracies)
        
        # Expected Calibration Error
        original_ece = self._calculate_expected_calibration_error(orig_conf, acc)
        calibrated_ece = self._calculate_expected_calibration_error(cal_conf, acc)
        
        # Brier Score
        original_brier = brier_score_loss(acc, orig_conf)
        calibrated_brier = brier_score_loss(acc, cal_conf)
        
        # Reliability diagram data
        reliability_diagram = self._create_reliability_diagram(cal_conf, acc)
        
        # Confidence histogram
        confidence_histogram = {}
        for i in range(10):
            bin_start = i * 0.1
            bin_end = (i + 1) * 0.1
            count = np.sum((cal_conf >= bin_start) & (cal_conf < bin_end))
            confidence_histogram[f"{bin_start:.1f}-{bin_end:.1f}"] = int(count)
        
        # Accuracy by confidence
        accuracy_by_confidence = {}
        for i in range(10):
            bin_start = i * 0.1
            bin_end = (i + 1) * 0.1
            in_bin = (cal_conf >= bin_start) & (cal_conf < bin_end)
            if np.sum(in_bin) > 0:
                accuracy_by_confidence[f"{bin_start:.1f}-{bin_end:.1f}"] = float(acc[in_bin].mean())
        
        print(f"  Original ECE: {original_ece:.3f}")
        print(f"  Calibrated ECE: {calibrated_ece:.3f}")
        print(f"  Improvement: {((original_ece - calibrated_ece) / original_ece * 100):+.1f}%")
        
        return CalibrationMetrics(
            expected_calibration_error=calibrated_ece,
            brier_score=calibrated_brier,
            log_likelihood=-log_loss(acc, cal_conf),
            reliability_diagram=reliability_diagram,
            confidence_histogram=confidence_histogram,
            accuracy_by_confidence=accuracy_by_confidence
        )
    
    def _create_reliability_diagram(self, confidences: np.ndarray, 
                                  accuracies: np.ndarray) -> Dict[str, Any]:
        """Create reliability diagram data."""
        
        bins = np.linspace(0, 1, 11)
        bin_centers = []
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []
        
        for i in range(len(bins) - 1):
            bin_start = bins[i]
            bin_end = bins[i + 1]
            in_bin = (confidences >= bin_start) & (confidences < bin_end)
            
            if np.sum(in_bin) > 0:
                bin_centers.append((bin_start + bin_end) / 2)
                bin_accuracies.append(float(accuracies[in_bin].mean()))
                bin_confidences.append(float(confidences[in_bin].mean()))
                bin_counts.append(int(np.sum(in_bin)))
        
        return {
            'bin_centers': bin_centers,
            'bin_accuracies': bin_accuracies,
            'bin_confidences': bin_confidences,
            'bin_counts': bin_counts
        }
    
    def save_calibration_models(self, filename: str):
        """Save trained calibration models."""
        
        data = {
            'isotonic_model': self.isotonic_model,
            'platt_model': self.platt_model,
            'temperature': self.temperature,
            'feature_calibrator': self.feature_calibrator,
            'feature_names': list(self.training_features[0].keys()) if self.training_features else []
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Calibration models saved to {filename}")
    
    def load_calibration_models(self, filename: str):
        """Load trained calibration models."""
        
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        self.isotonic_model = data['isotonic_model']
        self.platt_model = data['platt_model']
        self.temperature = data['temperature']
        self.feature_calibrator = data['feature_calibrator']
        
        print(f"📁 Calibration models loaded from {filename}")


def main():
    """Demo confidence calibration functionality."""
    
    print("🎯 CONFIDENCE CALIBRATION DEMO")
    print("=" * 50)
    
    # Create comprehensive test dataset
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from comprehensive_test_dataset import create_comprehensive_test_dataset
    test_cases = create_comprehensive_test_dataset()
    
    print(f"📝 Using {len(test_cases)} test cases")
    
    # Create calibrator
    calibrator = ConfidenceCalibrator()
    
    # Collect calibration data
    calibration_data = calibrator.collect_calibration_data(test_cases)
    
    # Train calibration models
    training_results = calibrator.train_calibration_models()
    
    # Evaluate calibration
    metrics = calibrator.evaluate_calibration(test_cases[:20], method="feature")  # Use subset for demo
    
    print(f"\n📊 Final Calibration Quality:")
    print(f"  Expected Calibration Error: {metrics.expected_calibration_error:.3f}")
    print(f"  Brier Score: {metrics.brier_score:.3f}")
    
    # Save models
    calibrator.save_calibration_models("confidence_calibration_models.pkl")
    
    return calibrator, metrics


if __name__ == "__main__":
    main()