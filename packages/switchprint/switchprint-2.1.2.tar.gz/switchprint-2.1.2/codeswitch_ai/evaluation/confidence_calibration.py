#!/usr/bin/env python3
"""Confidence calibration for code-switching detection models."""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import pickle
from collections import defaultdict
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from scipy.stats import chi2
import matplotlib.pyplot as plt
import seaborn as sns

from ..detection.ensemble_detector import EnsembleDetector
from ..detection.fasttext_detector import FastTextDetector
from ..detection.transformer_detector import TransformerDetector


@dataclass
class CalibrationMetrics:
    """Metrics for confidence calibration evaluation."""
    expected_calibration_error: float
    maximum_calibration_error: float
    average_confidence: float
    average_accuracy: float
    brier_score: float
    log_loss_score: float
    reliability_bins: List[Dict[str, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return asdict(self)
    
    def summary(self) -> str:
        """Generate summary report."""
        return f"""
Confidence Calibration Report:
=============================
Expected Calibration Error (ECE): {self.expected_calibration_error:.4f}
Maximum Calibration Error (MCE):  {self.maximum_calibration_error:.4f}
Average Confidence:               {self.average_confidence:.4f}
Average Accuracy:                 {self.average_accuracy:.4f}
Brier Score:                      {self.brier_score:.4f}
Log Loss:                         {self.log_loss_score:.4f}

Calibration Quality: {'Excellent' if self.expected_calibration_error < 0.05 else 'Good' if self.expected_calibration_error < 0.10 else 'Needs Improvement'}
"""


class ConfidenceCalibrator:
    """Dynamic confidence calibration for code-switching detection."""
    
    def __init__(self, num_bins: int = 10, method: str = "isotonic"):
        """Initialize confidence calibrator.
        
        Args:
            num_bins: Number of bins for calibration evaluation
            method: Calibration method ('isotonic', 'platt', 'beta')
        """
        self.num_bins = num_bins
        self.method = method
        self.calibrators = {}
        self.is_fitted = False
        
        # Text characteristics for dynamic calibration
        self.text_features = {
            'length': self._get_text_length,
            'multilingual_score': self._get_multilingual_score,
            'script_diversity': self._get_script_diversity,
            'punctuation_ratio': self._get_punctuation_ratio,
            'capitalization_ratio': self._get_capitalization_ratio,
            'digit_ratio': self._get_digit_ratio,
            'special_char_ratio': self._get_special_char_ratio
        }
        
        # Detector-specific calibration
        self.detector_calibrators = {}
        
    def _get_text_length(self, text: str) -> float:
        """Get normalized text length."""
        return min(len(text) / 100, 1.0)  # Normalize to [0, 1]
    
    def _get_multilingual_score(self, text: str) -> float:
        """Estimate multilingual content score."""
        # Simple heuristic: presence of different scripts
        scripts = set()
        for char in text:
            if char.isalpha():
                # Basic script detection
                if ord(char) < 128:
                    scripts.add('latin')
                elif 0x0600 <= ord(char) <= 0x06FF:
                    scripts.add('arabic')
                elif 0x4E00 <= ord(char) <= 0x9FFF:
                    scripts.add('cjk')
                elif 0x0900 <= ord(char) <= 0x097F:
                    scripts.add('devanagari')
                elif 0x0400 <= ord(char) <= 0x04FF:
                    scripts.add('cyrillic')
                else:
                    scripts.add('other')
        
        return min(len(scripts) / 3, 1.0)  # Normalize to [0, 1]
    
    def _get_script_diversity(self, text: str) -> float:
        """Calculate script diversity score."""
        char_types = {'latin': 0, 'digit': 0, 'space': 0, 'punct': 0, 'other': 0}
        
        for char in text:
            if char.isalpha() and ord(char) < 128:
                char_types['latin'] += 1
            elif char.isdigit():
                char_types['digit'] += 1
            elif char.isspace():
                char_types['space'] += 1
            elif char in '.,!?;:':
                char_types['punct'] += 1
            else:
                char_types['other'] += 1
        
        total = sum(char_types.values())
        if total == 0:
            return 0.0
        
        # Calculate entropy-based diversity
        entropy = 0
        for count in char_types.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return min(entropy / 2.32, 1.0)  # Normalize by log2(5)
    
    def _get_punctuation_ratio(self, text: str) -> float:
        """Get punctuation ratio."""
        if not text:
            return 0.0
        punct_count = sum(1 for char in text if char in '.,!?;:()[]{}"\'-')
        return punct_count / len(text)
    
    def _get_capitalization_ratio(self, text: str) -> float:
        """Get capitalization ratio."""
        if not text:
            return 0.0
        alpha_chars = [char for char in text if char.isalpha()]
        if not alpha_chars:
            return 0.0
        cap_count = sum(1 for char in alpha_chars if char.isupper())
        return cap_count / len(alpha_chars)
    
    def _get_digit_ratio(self, text: str) -> float:
        """Get digit ratio."""
        if not text:
            return 0.0
        digit_count = sum(1 for char in text if char.isdigit())
        return digit_count / len(text)
    
    def _get_special_char_ratio(self, text: str) -> float:
        """Get special character ratio."""
        if not text:
            return 0.0
        special_count = sum(1 for char in text if not char.isalnum() and not char.isspace())
        return special_count / len(text)
    
    def extract_features(self, texts: List[str]) -> np.ndarray:
        """Extract features for calibration.
        
        Args:
            texts: List of input texts
            
        Returns:
            Feature matrix
        """
        features = []
        
        for text in texts:
            text_features = []
            for feature_name, feature_func in self.text_features.items():
                try:
                    feature_value = feature_func(text)
                    text_features.append(feature_value)
                except Exception:
                    text_features.append(0.0)
            features.append(text_features)
        
        return np.array(features)
    
    def fit(self, texts: List[str], predictions: List[float], 
            ground_truth: List[bool], detector_name: str = "default") -> None:
        """Fit calibration model.
        
        Args:
            texts: Input texts
            predictions: Model predictions (probabilities)
            ground_truth: True labels
            detector_name: Name of detector for specific calibration
        """
        print(f"📊 Fitting confidence calibrator for {detector_name}")
        
        # Extract text features
        features = self.extract_features(texts)
        
        # Combine predictions with text features
        X = np.column_stack([predictions, features])
        y = np.array(ground_truth)
        
        # Fit calibration model
        if self.method == "isotonic":
            calibrator = IsotonicRegression(out_of_bounds='clip')
            X = X[:, 0]  # Use only the prediction column for isotonic regression
        elif self.method == "platt":
            calibrator = LogisticRegression()
        else:
            raise ValueError(f"Unknown calibration method: {self.method}")
        
        # Fit on combined features
        calibrator.fit(X, y)
        
        # Store calibrator
        self.detector_calibrators[detector_name] = calibrator
        self.is_fitted = True
        
        print(f"✓ Calibrator fitted for {detector_name}")
    
    def calibrate_confidence(self, text: str, prediction: float, 
                           detector_name: str = "default") -> float:
        """Calibrate confidence score.
        
        Args:
            text: Input text
            prediction: Raw prediction confidence
            detector_name: Name of detector
            
        Returns:
            Calibrated confidence score
        """
        if not self.is_fitted or detector_name not in self.detector_calibrators:
            # Return raw prediction if not calibrated
            return prediction
        
        # Extract features
        features = self.extract_features([text])[0]
        
        # Combine with prediction
        X = np.array([prediction] + features.tolist()).reshape(1, -1)
        
        # Get calibrated confidence
        calibrator = self.detector_calibrators[detector_name]
        
        if self.method == "isotonic":
            calibrated = calibrator.predict(X[:, 0])[0]  # Isotonic uses only prediction
        else:
            calibrated = calibrator.predict_proba(X)[0][1]  # Logistic regression
        
        return np.clip(calibrated, 0.0, 1.0)
    
    def evaluate_calibration(self, texts: List[str], predictions: List[float], 
                           ground_truth: List[bool], detector_name: str = "default") -> CalibrationMetrics:
        """Evaluate calibration quality.
        
        Args:
            texts: Input texts
            predictions: Model predictions
            ground_truth: True labels
            detector_name: Name of detector
            
        Returns:
            Calibration metrics
        """
        print(f"🔬 Evaluating calibration for {detector_name}")
        
        # Calibrate predictions if possible
        calibrated_predictions = []
        for text, pred in zip(texts, predictions):
            calibrated_pred = self.calibrate_confidence(text, pred, detector_name)
            calibrated_predictions.append(calibrated_pred)
        
        predictions = np.array(calibrated_predictions)
        ground_truth = np.array(ground_truth)
        
        # Calculate reliability diagram
        bin_boundaries = np.linspace(0, 1, self.num_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        reliability_bins = []
        ece = 0
        mce = 0
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find predictions in this bin
            in_bin = (predictions > bin_lower) & (predictions <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                # Calculate accuracy and confidence in this bin
                accuracy_in_bin = ground_truth[in_bin].mean()
                avg_confidence_in_bin = predictions[in_bin].mean()
                
                # Calculate calibration error
                calibration_error = abs(avg_confidence_in_bin - accuracy_in_bin)
                
                # Update ECE and MCE
                ece += prop_in_bin * calibration_error
                mce = max(mce, calibration_error)
                
                reliability_bins.append({
                    'bin_lower': bin_lower,
                    'bin_upper': bin_upper,
                    'accuracy': accuracy_in_bin,
                    'confidence': avg_confidence_in_bin,
                    'proportion': prop_in_bin,
                    'calibration_error': calibration_error
                })
        
        # Calculate other metrics
        avg_confidence = predictions.mean()
        avg_accuracy = ground_truth.mean()
        brier_score = brier_score_loss(ground_truth, predictions)
        
        # Avoid log(0) by clipping predictions
        predictions_clipped = np.clip(predictions, 1e-15, 1 - 1e-15)
        log_loss_score = log_loss(ground_truth, predictions_clipped)
        
        return CalibrationMetrics(
            expected_calibration_error=ece,
            maximum_calibration_error=mce,
            average_confidence=avg_confidence,
            average_accuracy=avg_accuracy,
            brier_score=brier_score,
            log_loss_score=log_loss_score,
            reliability_bins=reliability_bins
        )
    
    def plot_reliability_diagram(self, metrics: CalibrationMetrics, 
                               save_path: Optional[str] = None) -> None:
        """Plot reliability diagram.
        
        Args:
            metrics: Calibration metrics
            save_path: Optional path to save plot
        """
        try:
            plt.figure(figsize=(10, 8))
            
            # Extract data for plotting
            bin_centers = []
            accuracies = []
            confidences = []
            proportions = []
            
            for bin_info in metrics.reliability_bins:
                bin_center = (bin_info['bin_lower'] + bin_info['bin_upper']) / 2
                bin_centers.append(bin_center)
                accuracies.append(bin_info['accuracy'])
                confidences.append(bin_info['confidence'])
                proportions.append(bin_info['proportion'])
            
            if not bin_centers:
                print("⚠ No data for reliability diagram")
                return
            
            # Create subplot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
            
            # Reliability diagram
            ax1.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
            ax1.scatter(confidences, accuracies, s=[p * 1000 for p in proportions], 
                       alpha=0.7, label='Calibration Points')
            
            ax1.set_xlabel('Mean Predicted Probability')
            ax1.set_ylabel('Fraction of Positives')
            ax1.set_title('Reliability Diagram')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Add ECE and MCE text
            ax1.text(0.05, 0.95, f'ECE: {metrics.expected_calibration_error:.4f}', 
                    transform=ax1.transAxes, fontsize=12, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            ax1.text(0.05, 0.85, f'MCE: {metrics.maximum_calibration_error:.4f}', 
                    transform=ax1.transAxes, fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))
            
            # Confidence histogram
            if len(bin_centers) > 1:
                ax2.bar(bin_centers, proportions, width=0.08, alpha=0.7, 
                       color='skyblue', edgecolor='black')
                ax2.set_xlabel('Confidence')
                ax2.set_ylabel('Proportion of Samples')
                ax2.set_title('Confidence Distribution')
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"✓ Reliability diagram saved to {save_path}")
            else:
                plt.show()
                
        except Exception as e:
            print(f"⚠ Failed to plot reliability diagram: {e}")
    
    def save_calibrator(self, file_path: str) -> None:
        """Save calibrator to file.
        
        Args:
            file_path: Path to save calibrator
        """
        calibrator_data = {
            'method': self.method,
            'num_bins': self.num_bins,
            'is_fitted': self.is_fitted,
            'detector_calibrators': self.detector_calibrators
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(calibrator_data, f)
        
        print(f"✓ Calibrator saved to {file_path}")
    
    def load_calibrator(self, file_path: str) -> None:
        """Load calibrator from file.
        
        Args:
            file_path: Path to load calibrator from
        """
        with open(file_path, 'rb') as f:
            calibrator_data = pickle.load(f)
        
        self.method = calibrator_data['method']
        self.num_bins = calibrator_data['num_bins']
        self.is_fitted = calibrator_data['is_fitted']
        self.detector_calibrators = calibrator_data['detector_calibrators']
        
        print(f"✓ Calibrator loaded from {file_path}")


class DynamicConfidenceAdjuster:
    """Dynamic confidence adjustment based on runtime characteristics."""
    
    def __init__(self):
        """Initialize dynamic confidence adjuster."""
        self.adjustment_history = defaultdict(list)
        self.base_calibrator = ConfidenceCalibrator()
        
    def adjust_confidence(self, text: str, base_confidence: float, 
                         detector_name: str, context: Optional[Dict] = None) -> float:
        """Dynamically adjust confidence based on text characteristics.
        
        Args:
            text: Input text
            base_confidence: Base confidence from detector
            detector_name: Name of detector
            context: Optional context information
            
        Returns:
            Adjusted confidence score
        """
        # Start with base confidence
        adjusted_confidence = base_confidence
        
        # Adjust based on text characteristics
        text_len = len(text)
        
        # Length-based adjustment
        if text_len < 5:
            # Very short text - reduce confidence
            adjusted_confidence *= 0.8
        elif text_len < 15:
            # Short text - slight reduction
            adjusted_confidence *= 0.9
        elif text_len > 100:
            # Long text - slight increase
            adjusted_confidence *= 1.05
        
        # Script diversity adjustment
        script_diversity = self.base_calibrator._get_script_diversity(text)
        if script_diversity > 0.5:
            # High script diversity - might indicate code-switching
            adjusted_confidence *= 1.1
        
        # Punctuation adjustment
        punct_ratio = self.base_calibrator._get_punctuation_ratio(text)
        if punct_ratio > 0.2:
            # High punctuation - might reduce reliability
            adjusted_confidence *= 0.95
        
        # Context-based adjustment
        if context:
            # User language preferences
            if 'user_languages' in context:
                user_langs = context['user_languages']
                if len(user_langs) > 1:
                    # Multilingual user - increase confidence for mixed content
                    adjusted_confidence *= 1.05
            
            # Historical accuracy
            if 'historical_accuracy' in context:
                hist_acc = context['historical_accuracy']
                if hist_acc > 0.9:
                    # High historical accuracy - boost confidence
                    adjusted_confidence *= 1.02
                elif hist_acc < 0.7:
                    # Low historical accuracy - reduce confidence
                    adjusted_confidence *= 0.95
        
        # Ensure confidence stays in valid range
        adjusted_confidence = np.clip(adjusted_confidence, 0.0, 1.0)
        
        # Store adjustment for analysis
        adjustment = adjusted_confidence - base_confidence
        self.adjustment_history[detector_name].append({
            'text_length': text_len,
            'base_confidence': base_confidence,
            'adjusted_confidence': adjusted_confidence,
            'adjustment': adjustment
        })
        
        return adjusted_confidence
    
    def get_adjustment_statistics(self, detector_name: str) -> Dict[str, float]:
        """Get statistics about confidence adjustments.
        
        Args:
            detector_name: Name of detector
            
        Returns:
            Dictionary of adjustment statistics
        """
        if detector_name not in self.adjustment_history:
            return {}
        
        adjustments = [adj['adjustment'] for adj in self.adjustment_history[detector_name]]
        
        if not adjustments:
            return {}
        
        return {
            'mean_adjustment': np.mean(adjustments),
            'std_adjustment': np.std(adjustments),
            'positive_adjustments': sum(1 for adj in adjustments if adj > 0),
            'negative_adjustments': sum(1 for adj in adjustments if adj < 0),
            'total_adjustments': len(adjustments)
        }


def main():
    """Example usage of confidence calibration."""
    # Create synthetic data for demonstration
    np.random.seed(42)
    
    texts = [
        "Hello world",
        "Hola mundo", 
        "Hello, ¿cómo estás?",
        "Je suis très tired",
        "This is a longer text with mixed languages como esta frase",
        "Short text",
        "很好 very good indeed",
        "Привет! How are you?",
        "Normal English sentence",
        "Totally normal text here"
    ]
    
    # Simulate predictions and ground truth
    predictions = np.random.uniform(0.3, 0.95, len(texts))
    ground_truth = np.random.choice([0, 1], len(texts), p=[0.3, 0.7])
    
    # Initialize calibrator
    calibrator = ConfidenceCalibrator(method="isotonic")
    
    # Fit calibrator
    calibrator.fit(texts, predictions, ground_truth, "fasttext")
    
    # Evaluate calibration
    metrics = calibrator.evaluate_calibration(texts, predictions, ground_truth, "fasttext")
    print(metrics.summary())
    
    # Test dynamic adjustment
    adjuster = DynamicConfidenceAdjuster()
    
    for text, pred in zip(texts[:3], predictions[:3]):
        adjusted = adjuster.adjust_confidence(text, pred, "fasttext")
        print(f"Text: '{text[:30]}...'")
        print(f"Base: {pred:.3f} → Adjusted: {adjusted:.3f}")
        print()


if __name__ == "__main__":
    main()