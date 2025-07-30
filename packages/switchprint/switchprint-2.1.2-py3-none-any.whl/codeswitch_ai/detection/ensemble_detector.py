#!/usr/bin/env python3
"""Ensemble detector combining multiple language detection approaches."""

from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass
from functools import lru_cache

from .language_detector import LanguageDetector, DetectionResult
from .fasttext_detector import FastTextDetector
from .transformer_detector import TransformerDetector
from ..utils.thresholds import ThresholdConfig, DetectionMode


@dataclass
class EnsembleResult:
    """Result from ensemble detection."""
    detected_languages: List[str]
    confidence: float
    probabilities: Dict[str, float]
    method_results: Dict[str, DetectionResult]
    ensemble_weights: Dict[str, float]
    switch_points: List[Tuple[int, str, str, float]]
    phrases: List[Dict[str, Any]]
    final_method: str
    quality_info: Optional[Dict[str, Any]] = None  # New field for quality validation


class EnsembleDetector(LanguageDetector):
    """Ensemble detector combining FastText, Transformer, and rule-based methods."""
    
    def __init__(self, 
                 use_fasttext: bool = True,
                 use_transformer: bool = True,
                 transformer_model: str = "bert-base-multilingual-cased",
                 ensemble_strategy: str = "weighted_average",
                 cache_size: int = 1000,
                 threshold_mode: DetectionMode = DetectionMode.BALANCED,
                 custom_thresholds: Optional[ThresholdConfig] = None,
                 short_text_fallback: bool = True):
        """Initialize ensemble detector.
        
        Args:
            use_fasttext: Whether to use FastText detector
            use_transformer: Whether to use transformer detector
            transformer_model: Which transformer model to use
            ensemble_strategy: Strategy for combining results ('weighted_average', 'voting', 'confidence_based')
            cache_size: Size of LRU cache
            threshold_mode: Detection mode for threshold configuration
            custom_thresholds: Custom threshold configuration (overrides threshold_mode)
            short_text_fallback: Enable transformer fallback for short texts when use_transformer=False
        """
        super().__init__()
        
        self.use_fasttext = use_fasttext
        self.use_transformer = use_transformer
        self.ensemble_strategy = ensemble_strategy
        self.short_text_fallback = short_text_fallback
        self.detector_type = "ensemble"  # Add detector type attribute
        
        # Initialize threshold configuration
        if custom_thresholds:
            self.threshold_config = custom_thresholds
        else:
            self.threshold_config = ThresholdConfig(threshold_mode)
        
        # Initialize detectors
        self.detectors = {}
        
        if use_fasttext:
            try:
                self.detectors['fasttext'] = FastTextDetector(cache_size=cache_size)
                print("✓ FastText detector loaded")
            except Exception as e:
                print(f"⚠ FastText detector failed to load: {e}")
        
        if use_transformer:
            try:
                self.detectors['transformer'] = TransformerDetector(
                    model_name=transformer_model,
                    cache_size=cache_size
                )
                print("✓ Transformer detector loaded")
            except Exception as e:
                print(f"⚠ Transformer detector failed to load: {e}")
        
        # Rule-based detector (minimal weight to avoid degrading performance)
        self.detectors['rules'] = self._create_rule_based_detector()
        
        # Ensemble weights (can be learned/tuned)
        # Reduced rule weight since FastText performs excellently
        self.base_weights = {
            'fasttext': 0.7,
            'transformer': 0.25,
            'rules': 0.05
        }
        
        # Dynamic weight adjustment factors
        self.weight_adjustments = {
            'short_text': {'fasttext': 1.2, 'rules': 1.1},  # FastText better for short text
            'long_text': {'transformer': 1.2},  # Transformer better for long text
            'mixed_script': {'transformer': 1.3},  # Transformer better for mixed scripts
            'user_guidance': {'all': 1.1}  # Slight boost when user provides guidance
        }
    
    def _create_rule_based_detector(self) -> 'RuleBasedDetector':
        """Create rule-based detector."""
        return RuleBasedDetector()
    
    def _calculate_dynamic_weights(self, 
                                  text: str, 
                                  user_languages: Optional[List[str]] = None) -> Dict[str, float]:
        """Calculate dynamic weights based on text characteristics."""
        weights = self.base_weights.copy()
        
        # Remove weights for unavailable detectors
        weights = {k: v for k, v in weights.items() if k in self.detectors}
        
        # Text length considerations
        if len(text.split()) < 5:
            # Short text
            for detector, factor in self.weight_adjustments.get('short_text', {}).items():
                if detector in weights:
                    weights[detector] *= factor
        elif len(text.split()) > 50:
            # Long text
            for detector, factor in self.weight_adjustments.get('long_text', {}).items():
                if detector in weights:
                    weights[detector] *= factor
        
        # Mixed script detection
        if self._has_mixed_scripts(text):
            for detector, factor in self.weight_adjustments.get('mixed_script', {}).items():
                if detector in weights:
                    weights[detector] *= factor
        
        # User guidance boost
        if user_languages:
            factor = self.weight_adjustments.get('user_guidance', {}).get('all', 1.0)
            weights = {k: v * factor for k, v in weights.items()}
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def _has_mixed_scripts(self, text: str) -> bool:
        """Check if text contains mixed scripts."""
        import re
        
        scripts = {
            'latin': r'[a-zA-Z]',
            'chinese': r'[\u4e00-\u9fff]',
            'arabic': r'[\u0600-\u06ff]',
            'cyrillic': r'[\u0400-\u04ff]',
            'devanagari': r'[\u0900-\u097f]'
        }
        
        found_scripts = []
        for script_name, pattern in scripts.items():
            if re.search(pattern, text):
                found_scripts.append(script_name)
        
        return len(found_scripts) > 1
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> EnsembleResult:
        """Detect language using ensemble approach."""
        if not text.strip():
            # Handle empty text with proper quality info
            empty_quality = self.threshold_config.validate_confidence([], 0.0, 0)
            return EnsembleResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method_results={},
                ensemble_weights={},
                switch_points=[],
                phrases=[],
                final_method='ensemble-empty',
                quality_info=empty_quality
            )
        
        # Check if we need transformer fallback for short text
        text_length = len(text.split())
        is_short_text = text_length < 5
        
        # Get results from each detector (with short text fallback logic)
        method_results = {}
        active_detectors = self.detectors.copy()
        
        # Enable transformer fallback for short texts if configured
        if (is_short_text and self.short_text_fallback and 
            not self.use_transformer and 'transformer' not in active_detectors):
            try:
                # Temporarily load transformer for short text
                active_detectors['transformer'] = TransformerDetector(cache_size=100)
                print("⚡ Enabled transformer fallback for short text")
            except Exception as e:
                print(f"⚠ Could not enable transformer fallback: {e}")
        
        for name, detector in active_detectors.items():
            try:
                result = detector.detect_language(text, user_languages)
                method_results[name] = result
            except Exception as e:
                print(f"Error with {name} detector: {e}")
                continue
        
        if not method_results:
            return EnsembleResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method_results={},
                ensemble_weights={},
                switch_points=[],
                phrases=[],
                final_method='ensemble-error'
            )
        
        # Calculate dynamic weights
        ensemble_weights = self._calculate_dynamic_weights(text, user_languages)
        
        # Combine results based on strategy
        combined_result = self._combine_results(method_results, ensemble_weights)
        
        # Detect switch points (if transformer available)
        switch_points = []
        # Skip switch point detection for now to avoid recursion issues
        # if 'transformer' in self.detectors:
        #     try:
        #         switch_points = self.detectors['transformer'].detect_code_switching_points(text)
        #     except Exception as e:
        #         print(f"Error detecting switch points: {e}")
        
        # Create phrase clusters
        phrases = self._create_phrase_clusters(text, combined_result['probabilities'])
        
        # Validate confidence and get quality information
        text_length = len(text.split()) if text.strip() else 0
        quality_info = self.threshold_config.validate_confidence(
            combined_result['languages'], 
            combined_result['confidence'],
            text_length
        )
        
        return EnsembleResult(
            detected_languages=combined_result['languages'],
            confidence=combined_result['confidence'],
            probabilities=combined_result['probabilities'],
            method_results=method_results,
            ensemble_weights=ensemble_weights,
            switch_points=switch_points,
            phrases=phrases,
            final_method='ensemble-' + self.ensemble_strategy,
            quality_info=quality_info
        )
    
    def _combine_results(self, 
                        method_results: Dict[str, DetectionResult], 
                        weights: Dict[str, float]) -> Dict[str, Any]:
        """Combine results from different methods."""
        if self.ensemble_strategy == "weighted_average":
            return self._weighted_average_combination(method_results, weights)
        elif self.ensemble_strategy == "voting":
            return self._voting_combination(method_results, weights)
        elif self.ensemble_strategy == "confidence_based":
            return self._confidence_based_combination(method_results, weights)
        else:
            return self._weighted_average_combination(method_results, weights)
    
    def _weighted_average_combination(self, 
                                    method_results: Dict[str, DetectionResult], 
                                    weights: Dict[str, float]) -> Dict[str, Any]:
        """Combine using weighted average of probabilities."""
        combined_probs = {}
        total_confidence = 0.0
        
        for method_name, result in method_results.items():
            weight = weights.get(method_name, 0.0)
            
            if weight > 0:
                # Add weighted probabilities
                for lang, prob in result.probabilities.items():
                    if lang not in combined_probs:
                        combined_probs[lang] = 0.0
                    combined_probs[lang] += prob * weight
                
                # Add weighted confidence
                total_confidence += result.confidence * weight
        
        if not combined_probs:
            return {'languages': [], 'confidence': 0.0, 'probabilities': {}}
        
        # Get all languages above dynamic threshold
        threshold = self.threshold_config.get_inclusion_threshold()
        detected_languages = [lang for lang, prob in combined_probs.items() if prob > threshold]
        detected_languages = sorted(detected_languages, key=lambda lang: combined_probs[lang], reverse=True)
        
        # (B) Language Pair Validation: Apply validation and penalization
        detected_languages = self._validate_language_pairs(detected_languages, combined_probs)
        
        # Calculate overall confidence as the maximum probability (not sum, which can exceed 1.0)
        overall_confidence = max(combined_probs[lang] for lang in detected_languages) if detected_languages else 0.0
        
        return {
            'languages': detected_languages,
            'confidence': overall_confidence,
            'probabilities': combined_probs
        }
    
    def _voting_combination(self, 
                           method_results: Dict[str, DetectionResult], 
                           weights: Dict[str, float]) -> Dict[str, Any]:
        """Combine using weighted voting."""
        votes = {}
        
        for method_name, result in method_results.items():
            weight = weights.get(method_name, 0.0)
            
            if result.detected_languages and weight > 0:
                lang = result.detected_languages[0]
                if lang not in votes:
                    votes[lang] = 0.0
                votes[lang] += weight * result.confidence
        
        if not votes:
            return {'languages': [], 'confidence': 0.0, 'probabilities': {}}
        
        # Get winner
        winner = max(votes.keys(), key=lambda k: votes[k])
        max_vote = votes[winner]
        
        # Normalize votes to probabilities
        total_votes = sum(votes.values())
        probabilities = {k: v / total_votes for k, v in votes.items()} if total_votes > 0 else {}
        
        return {
            'languages': [winner],
            'confidence': max_vote,
            'probabilities': probabilities
        }
    
    def _confidence_based_combination(self, 
                                    method_results: Dict[str, DetectionResult], 
                                    weights: Dict[str, float]) -> Dict[str, Any]:
        """Combine based on confidence scores."""
        # Find the method with highest weighted confidence
        best_method = None
        best_score = 0.0
        
        for method_name, result in method_results.items():
            weight = weights.get(method_name, 0.0)
            weighted_confidence = result.confidence * weight
            
            if weighted_confidence > best_score:
                best_score = weighted_confidence
                best_method = method_name
        
        if best_method is None:
            return {'languages': [], 'confidence': 0.0, 'probabilities': {}}
        
        best_result = method_results[best_method]
        
        return {
            'languages': best_result.detected_languages,
            'confidence': best_result.confidence,
            'probabilities': best_result.probabilities
        }
    
    def _validate_language_pairs(self, detected_languages: List[str], probabilities: Dict[str, float]) -> List[str]:
        """Validate and filter unlikely language combinations."""
        if len(detected_languages) <= 1:
            return detected_languages
        
        # (B) Language Pair Validation: Define unlikely pairs
        INVALID_PAIRS = {
            frozenset(['fr', 'sw']),  # French + Swahili 
            frozenset(['es', 'ja']),  # Spanish + Japanese
            frozenset(['de', 'zh']),  # German + Chinese
            frozenset(['en', 'th']),  # English + Thai (unless in Thailand)
            frozenset(['it', 'vi']),  # Italian + Vietnamese
        }
        
        # Common code-switching pairs (prioritize these)
        COMMON_PAIRS = {
            frozenset(['en', 'es']),  # English + Spanish
            frozenset(['en', 'fr']),  # English + French
            frozenset(['en', 'de']),  # English + German
            frozenset(['es', 'pt']),  # Spanish + Portuguese
            frozenset(['hi', 'en']),  # Hindi + English
            frozenset(['zh', 'en']),  # Chinese + English
        }
        
        # Check for invalid pairs and penalize
        lang_set = frozenset(detected_languages[:2])  # Check top 2 languages
        
        if lang_set in INVALID_PAIRS:
            # Keep only the highest confidence language
            return [detected_languages[0]]
        
        if lang_set in COMMON_PAIRS:
            # Boost confidence for common pairs (already selected, just return as-is)
            return detected_languages
        
        # For other pairs, apply conservative filtering if confidence gap is small
        if len(detected_languages) >= 2:
            primary_conf = probabilities.get(detected_languages[0], 0)
            secondary_conf = probabilities.get(detected_languages[1], 0)
            
            # If secondary language has very low confidence relative to primary, remove it
            if secondary_conf < primary_conf * 0.3:
                return [detected_languages[0]]
        
        return detected_languages
    
    def _create_phrase_clusters(self, text: str, probabilities: Dict[str, float]) -> List[Dict[str, Any]]:
        """Create phrase clusters based on language probabilities."""
        words = text.split()
        if not words:
            return []
        
        # Simple clustering: assign all words to top language
        if probabilities:
            top_lang = max(probabilities.keys(), key=lambda k: probabilities[k])
            top_conf = probabilities[top_lang]
            
            return [{
                'text': text,
                'language': top_lang,
                'confidence': top_conf,
                'words': words,
                'start_index': 0,
                'end_index': len(words) - 1
            }]
        
        return []
    
    def get_detector_info(self) -> Dict[str, Any]:
        """Get information about all loaded detectors."""
        info = {
            'ensemble_strategy': self.ensemble_strategy,
            'base_weights': self.base_weights,
            'detectors': {}
        }
        
        for name, detector in self.detectors.items():
            try:
                if hasattr(detector, 'get_model_info'):
                    info['detectors'][name] = detector.get_model_info()
                else:
                    info['detectors'][name] = {'type': type(detector).__name__}
            except Exception as e:
                info['detectors'][name] = {'error': str(e)}
        
        return info


class RuleBasedDetector(LanguageDetector):
    """Simple rule-based detector as fallback."""
    
    def __init__(self):
        super().__init__()
        
        # Common function words by language
        self.function_words = {
            'en': ['the', 'and', 'is', 'to', 'a', 'in', 'that', 'it', 'of', 'for'],
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'it': ['il', 'di', 'che', 'e', 'la', 'per', 'in', 'un', 'è', 'con'],
            'pt': ['o', 'de', 'e', 'que', 'a', 'do', 'da', 'em', 'um', 'para'],
            'ru': ['и', 'в', 'не', 'на', 'с', 'что', 'а', 'по', 'как', 'из'],
        }
        
        # Script patterns
        self.script_patterns = {
            'zh': r'[\u4e00-\u9fff]',
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',
            'ko': r'[\uac00-\ud7af]',
            'ar': r'[\u0600-\u06ff]',
            'hi': r'[\u0900-\u097f]',
            'ru': r'[\u0400-\u04ff]',
            'el': r'[\u0370-\u03ff]',
            'he': r'[\u0590-\u05ff]',
            'th': r'[\u0e00-\u0e7f]',
        }
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> DetectionResult:
        """Simple rule-based language detection."""
        import re
        
        if not text.strip():
            return DetectionResult([], 0.0, {}, 'rules')
        
        text_lower = text.lower()
        scores = {}
        
        # Script-based detection (high confidence)
        for lang, pattern in self.script_patterns.items():
            if re.search(pattern, text):
                scores[lang] = 0.9
        
        # If no script match, use function words
        if not scores:
            for lang, words in self.function_words.items():
                count = sum(1 for word in words if word in text_lower)
                if count > 0:
                    scores[lang] = min(0.8, count * 0.1)
        
        if not scores:
            return DetectionResult([], 0.0, {}, 'rules')
        
        # Get best match
        best_lang = max(scores.keys(), key=lambda k: scores[k])
        best_score = scores[best_lang]
        
        return DetectionResult(
            detected_languages=[best_lang],
            confidence=best_score,
            probabilities=scores,
            method='rules'
        )