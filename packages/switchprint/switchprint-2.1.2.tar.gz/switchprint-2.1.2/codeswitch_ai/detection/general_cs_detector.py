#!/usr/bin/env python3
"""
General Code-Switching Detector

A general-purpose code-switching detector that:
1. Works across any language pairs (not specific to Hindi-English)
2. Fixes the ensemble sabotage issues we discovered
3. Provides observability for further refinement
4. Serves as a launching pad for specialized improvements

Key principles:
- Language-agnostic approach
- No hard-coded language pair restrictions
- Rich observability and debugging info
- Modular design for easy refinement
"""

import re
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import json
from functools import lru_cache

from .language_detector import LanguageDetector, DetectionResult
from .fasttext_detector import FastTextDetector
from ..utils.thresholds import ThresholdConfig, DetectionMode

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

@dataclass
class WordAnalysis:
    """Analysis of a single word."""
    word: str
    position: int
    fasttext_prediction: str
    fasttext_confidence: float
    transformer_prediction: Optional[str]
    transformer_confidence: Optional[float]
    final_prediction: str
    final_confidence: float
    reasoning: str

@dataclass
class GeneralCSResult:
    """Rich result with observability for general code-switching detection."""
    detected_languages: List[str]
    confidence: float
    probabilities: Dict[str, float]
    word_analyses: List[WordAnalysis]
    switch_points: List[Dict[str, Any]]
    method: str
    is_code_mixed: bool
    quality_metrics: Dict[str, Any]
    debug_info: Dict[str, Any]
    
    def to_detection_result(self) -> DetectionResult:
        """Convert to standard DetectionResult for API compatibility."""
        return DetectionResult(
            detected_languages=self.detected_languages,
            confidence=self.confidence,
            probabilities=self.probabilities,
            method=self.method,
            switch_points=[sp.get('position', 0) for sp in self.switch_points],
            token_languages=[wa.final_prediction for wa in self.word_analyses if wa.final_prediction != 'unknown']
        )

class GeneralCodeSwitchingDetector(LanguageDetector):
    """
    General-purpose code-switching detector with rich observability.
    
    Fixes the ensemble sabotage issues while maintaining language generality.
    Provides extensive debugging information for refinement.
    """
    
    def __init__(self,
                 use_transformer: bool = True, 
                 transformer_model: str = "papluca/xlm-roberta-base-language-detection",
                 threshold_mode: DetectionMode = DetectionMode.HIGH_RECALL,
                 enable_word_analysis: bool = True,
                 min_confidence_for_detection: float = 0.3,
                 performance_mode: str = "balanced",
                 detector_mode: str = "code_switching"):
        """Initialize general code-switching detector.
        
        Args:
            use_transformer: Whether to use transformer for context
            transformer_model: General multilingual model to use
            threshold_mode: Detection threshold mode (HIGH_RECALL recommended for CS)
            enable_word_analysis: Enable word-level analysis for CS detection
            min_confidence_for_detection: Minimum confidence to include a language
            performance_mode: "fast" (FastText only), "balanced" (optimized), "accurate" (full analysis)
            detector_mode: "code_switching" (optimized for CS), "monolingual" (optimized for single language), "multilingual" (general multilingual)
        """
        super().__init__()
        
        # Configuration
        self.enable_word_analysis = enable_word_analysis
        self.min_confidence = min_confidence_for_detection
        self.detector_mode = detector_mode
        
        # Configure detector based on mode
        if detector_mode == "monolingual":
            # Optimized for single language detection
            self.enable_word_analysis = False  # Disable word analysis for speed
            threshold_mode = DetectionMode.HIGH_PRECISION  # Higher precision for monolingual
            self.min_confidence = 0.5  # Higher confidence threshold
        elif detector_mode == "multilingual":
            # General multilingual but not optimized for code-switching
            threshold_mode = DetectionMode.BALANCED
            self.min_confidence = 0.4
        # else: "code_switching" keeps original settings
        
        # Performance optimization settings based on mode
        self.performance_mode = performance_mode
        if performance_mode == "fast":
            self.use_word_caching = True
            self.word_cache = {}
            self.batch_transformer_analysis = False
            self.max_words_for_transformer = 0  # No transformer for words
            use_transformer = False  # Override transformer setting
        elif performance_mode == "balanced":
            self.use_word_caching = True
            self.word_cache = {}
            self.batch_transformer_analysis = True
            self.max_words_for_transformer = 10
        else:  # accurate
            self.use_word_caching = True
            self.word_cache = {}
            self.batch_transformer_analysis = False
            self.max_words_for_transformer = 50
        
        # Initialize threshold configuration (use HIGH_RECALL to avoid ensemble sabotage)
        self.threshold_config = ThresholdConfig(threshold_mode)
        
        # Initialize FastText detector
        self.fasttext = FastTextDetector()
        
        # Initialize transformer (optional, for context)
        self.transformer = None
        if use_transformer and TRANSFORMERS_AVAILABLE:
            try:
                self.transformer = pipeline(
                    "text-classification",
                    model=transformer_model
                )
                print(f"✓ General CS detector initialized with transformer: {transformer_model}")
            except Exception as e:
                print(f"⚠ Transformer unavailable, using FastText only: {e}")
        else:
            print("✓ General CS detector initialized (FastText only)")
        
        print(f"  Detector mode: {detector_mode}")
        print(f"  Performance mode: {performance_mode}")
        print(f"  Threshold mode: {threshold_mode.value}")
        print(f"  Word analysis: {'Enabled' if self.enable_word_analysis else 'Disabled'}")
        print(f"  Min confidence: {self.min_confidence}")
        print(f"  Max words for transformer: {self.max_words_for_transformer}")
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> GeneralCSResult:
        """Detect code-switching using general approach with rich observability."""
        if not text.strip():
            return self._create_empty_result()
        
        debug_info = {
            "input_text": text,
            "text_length": len(text),
            "word_count": len(text.split()),
            "user_languages": user_languages
        }
        
        # Step 1: Get overall text-level prediction
        text_level_result = self._get_text_level_prediction(text)
        debug_info["text_level_prediction"] = text_level_result
        
        # Step 2: Word-level analysis (if enabled)
        word_analyses = []
        if self.enable_word_analysis:
            word_analyses = self._analyze_words(text)
            debug_info["word_level_analysis"] = {
                "total_words": len(word_analyses),
                "words_analyzed": len([w for w in word_analyses if w.final_prediction != 'unknown'])
            }
        
        # Step 3: Combine evidence WITHOUT ensemble sabotage
        final_result = self._combine_evidence_safely(text_level_result, word_analyses, text, debug_info)
        
        # Step 4: Rich observability
        final_result.debug_info = debug_info
        final_result.quality_metrics = self._calculate_quality_metrics(final_result, text)
        
        return final_result
    
    def detect_language_standard(self, text: str, user_languages: Optional[List[str]] = None) -> DetectionResult:
        """Detect language with standard DetectionResult for API compatibility."""
        result = self.detect_language(text, user_languages)
        return result.to_detection_result()
    
    def _get_text_level_prediction(self, text: str) -> Dict[str, Any]:
        """Get text-level language prediction."""
        # FastText prediction
        ft_result = self.fasttext.detect_language(text)
        
        text_prediction = {
            "fasttext": {
                "languages": ft_result.detected_languages,
                "confidence": ft_result.confidence,
                "probabilities": ft_result.probabilities
            }
        }
        
        # Transformer prediction (if available)
        if self.transformer:
            try:
                trans_result = self.transformer(text)
                if isinstance(trans_result, list):
                    trans_result = trans_result[0]
                
                text_prediction["transformer"] = {
                    "language": trans_result['label'].lower(),
                    "confidence": trans_result['score']
                }
            except Exception as e:
                text_prediction["transformer"] = {"error": str(e)}
        
        return text_prediction
    
    def _analyze_words(self, text: str) -> List[WordAnalysis]:
        """Analyze individual words for language detection with performance optimizations."""
        words = re.findall(r'\b\w+\b', text)  # Extract words
        word_analyses = []
        
        # Filter and prepare words for analysis
        words_to_analyze = [(i, word) for i, word in enumerate(words) if len(word) >= 2]
        
        if not words_to_analyze:
            return word_analyses
        
        # Get FastText predictions for all words (this is fast)
        ft_predictions = self._get_fasttext_predictions(words_to_analyze)
        
        # Get transformer predictions (with optimizations)
        trans_predictions = self._get_transformer_predictions(words_to_analyze) if self.transformer else {}
        
        # Combine results
        for i, word in words_to_analyze:
            ft_lang, ft_conf = ft_predictions.get(word, ('unknown', 0.0))
            trans_lang, trans_conf = trans_predictions.get(word, (None, None))
            
            # Decide final prediction
            final_lang, final_conf, reasoning = self._decide_word_prediction(
                ft_lang, ft_conf, trans_lang, trans_conf
            )
            
            word_analysis = WordAnalysis(
                word=word,
                position=i,
                fasttext_prediction=ft_lang,
                fasttext_confidence=ft_conf,
                transformer_prediction=trans_lang,
                transformer_confidence=trans_conf,
                final_prediction=final_lang,
                final_confidence=final_conf,
                reasoning=reasoning
            )
            
            word_analyses.append(word_analysis)
        
        return word_analyses
    
    def _get_fasttext_predictions(self, words_to_analyze: List[Tuple[int, str]]) -> Dict[str, Tuple[str, float]]:
        """Get FastText predictions for words with caching."""
        predictions = {}
        
        for i, word in words_to_analyze:
            # Check cache first
            if self.use_word_caching and word.lower() in self.word_cache:
                predictions[word] = self.word_cache[word.lower()]
                continue
            
            # Get FastText prediction
            try:
                ft_result = self.fasttext.detect_language(word)
                ft_lang = ft_result.detected_languages[0] if ft_result.detected_languages else 'unknown'
                ft_conf = ft_result.confidence
                result = (ft_lang, ft_conf)
                
                # Cache result for future use
                if self.use_word_caching:
                    self.word_cache[word.lower()] = result
                
                predictions[word] = result
            except:
                predictions[word] = ('unknown', 0.0)
        
        return predictions
    
    def _get_transformer_predictions(self, words_to_analyze: List[Tuple[int, str]]) -> Dict[str, Tuple[Optional[str], Optional[float]]]:
        """Get transformer predictions with performance optimizations."""
        predictions = {}
        
        # Limit transformer analysis for performance
        if len(words_to_analyze) > self.max_words_for_transformer:
            # Only analyze first N words and last N words
            words_to_analyze = words_to_analyze[:self.max_words_for_transformer//2] + words_to_analyze[-self.max_words_for_transformer//2:]
        
        # Batch process if possible (not all transformers support this well)
        if self.batch_transformer_analysis and len(words_to_analyze) <= 5:
            try:
                words = [word for i, word in words_to_analyze]
                results = self.transformer(words)
                
                for (i, word), result in zip(words_to_analyze, results):
                    if isinstance(result, list):
                        result = result[0]
                    predictions[word] = (result['label'].lower(), result['score'])
                    
            except Exception as e:
                # Fall back to individual processing
                return self._get_transformer_predictions_individual(words_to_analyze)
        else:
            return self._get_transformer_predictions_individual(words_to_analyze)
        
        return predictions
    
    def _get_transformer_predictions_individual(self, words_to_analyze: List[Tuple[int, str]]) -> Dict[str, Tuple[Optional[str], Optional[float]]]:
        """Get transformer predictions individually."""
        predictions = {}
        
        for i, word in words_to_analyze:
            try:
                trans_result = self.transformer(word)
                if isinstance(trans_result, list):
                    trans_result = trans_result[0]
                predictions[word] = (trans_result['label'].lower(), trans_result['score'])
            except:
                predictions[word] = (None, None)
        
        return predictions
    
    def _decide_word_prediction(self, ft_lang: str, ft_conf: float,
                              trans_lang: Optional[str], trans_conf: Optional[float]) -> Tuple[str, float, str]:
        """Decide final word prediction from multiple sources."""
        
        # If only FastText available
        if trans_lang is None:
            if ft_conf >= self.min_confidence:
                return ft_lang, ft_conf, "fasttext_only"
            else:
                return 'unknown', ft_conf, "low_confidence"
        
        # Both available - simple confidence-based decision
        if ft_conf >= trans_conf:
            if ft_conf >= self.min_confidence:
                return ft_lang, ft_conf, "fasttext_higher_confidence"
            else:
                return 'unknown', ft_conf, "both_low_confidence"
        else:
            if trans_conf >= self.min_confidence:
                return trans_lang, trans_conf, "transformer_higher_confidence"
            else:
                return 'unknown', trans_conf, "both_low_confidence"
    
    def _combine_evidence_safely(self, text_level: Dict, word_analyses: List[WordAnalysis], 
                                text: str, debug_info: Dict) -> GeneralCSResult:
        """Combine evidence WITHOUT ensemble sabotage."""
        
        # Start with text-level languages as base
        ft_text_result = text_level["fasttext"]
        base_languages = ft_text_result["languages"]
        base_probabilities = ft_text_result["probabilities"].copy()
        
        # Add evidence from word-level analysis
        if word_analyses:
            word_language_votes = {}
            total_word_confidence = 0.0
            
            for word_analysis in word_analyses:
                if word_analysis.final_prediction != 'unknown':
                    lang = word_analysis.final_prediction
                    conf = word_analysis.final_confidence
                    
                    if lang not in word_language_votes:
                        word_language_votes[lang] = 0.0
                    word_language_votes[lang] += conf
                    total_word_confidence += conf
            
            # Normalize word votes to probabilities
            word_probabilities = {}
            if total_word_confidence > 0:
                for lang, votes in word_language_votes.items():
                    word_probabilities[lang] = votes / total_word_confidence
            
            debug_info["word_probabilities"] = word_probabilities
            
            # Combine text and word evidence (NO SABOTAGE)
            combined_probs = base_probabilities.copy()
            
            # Add word evidence as additional signal (not replacement)
            for lang, word_prob in word_probabilities.items():
                if lang in combined_probs:
                    # Boost existing language
                    combined_probs[lang] = min(1.0, combined_probs[lang] + word_prob * 0.3)
                else:
                    # Add new language found at word level
                    combined_probs[lang] = word_prob * 0.5
            
            base_probabilities = combined_probs
        
        # Apply threshold to determine final languages (use HIGH_RECALL threshold)
        threshold = self.threshold_config.get_inclusion_threshold()
        detected_languages = []
        
        for lang, prob in base_probabilities.items():
            if prob >= threshold:
                detected_languages.append(lang)
        
        # Sort by probability
        detected_languages.sort(key=lambda l: base_probabilities[l], reverse=True)
        
        # Ensure at least one language if we have reasonable evidence
        if not detected_languages and base_probabilities:
            best_lang = max(base_probabilities.keys(), key=lambda l: base_probabilities[l])
            if base_probabilities[best_lang] >= 0.1:  # Very low threshold for fallback
                detected_languages = [best_lang]
        
        # Find switch points
        switch_points = self._find_switch_points(word_analyses)
        
        # Calculate confidence
        if detected_languages:
            overall_confidence = max(base_probabilities[lang] for lang in detected_languages)
        else:
            overall_confidence = 0.0
        
        # Determine if code-mixed
        is_code_mixed = len(detected_languages) > 1 and len(switch_points) > 0
        
        return GeneralCSResult(
            detected_languages=detected_languages,
            confidence=overall_confidence,
            probabilities=base_probabilities,
            word_analyses=word_analyses,
            switch_points=switch_points,
            method="general-cs-safe-combination",
            is_code_mixed=is_code_mixed,
            quality_metrics={},  # Will be filled later
            debug_info={}  # Will be filled later
        )
    
    def _find_switch_points(self, word_analyses: List[WordAnalysis]) -> List[Dict[str, Any]]:
        """Find language switch points with rich information."""
        if len(word_analyses) < 2:
            return []
        
        switch_points = []
        prev_lang = None
        
        for i, analysis in enumerate(word_analyses):
            current_lang = analysis.final_prediction
            
            if (prev_lang and 
                current_lang != prev_lang and 
                current_lang != 'unknown' and 
                prev_lang != 'unknown' and
                analysis.final_confidence >= 0.4):  # Reasonable threshold for switches
                
                switch_point = {
                    "position": i,
                    "from_language": prev_lang,
                    "to_language": current_lang,
                    "word": analysis.word,
                    "confidence": analysis.final_confidence,
                    "context": {
                        "previous_word": word_analyses[i-1].word if i > 0 else None,
                        "current_word": analysis.word
                    }
                }
                switch_points.append(switch_point)
            
            if current_lang != 'unknown':
                prev_lang = current_lang
        
        return switch_points
    
    def _calculate_quality_metrics(self, result: GeneralCSResult, text: str) -> Dict[str, Any]:
        """Calculate quality metrics for observability."""
        metrics = {
            "detection_confidence": result.confidence,
            "languages_detected": len(result.detected_languages),
            "switch_points_found": len(result.switch_points),
            "text_length": len(text),
            "word_count": len(text.split())
        }
        
        if result.word_analyses:
            analyzed_words = len(result.word_analyses)
            unknown_words = len([w for w in result.word_analyses if w.final_prediction == 'unknown'])
            
            metrics.update({
                "word_analysis_coverage": (analyzed_words - unknown_words) / analyzed_words if analyzed_words > 0 else 0,
                "avg_word_confidence": np.mean([w.final_confidence for w in result.word_analyses]) if result.word_analyses else 0,
                "method_distribution": self._get_method_distribution(result.word_analyses)
            })
        
        return metrics
    
    def _get_method_distribution(self, word_analyses: List[WordAnalysis]) -> Dict[str, int]:
        """Get distribution of methods used for word analysis."""
        distribution = {}
        for analysis in word_analyses:
            method = analysis.reasoning
            distribution[method] = distribution.get(method, 0) + 1
        return distribution
    
    def _create_empty_result(self) -> GeneralCSResult:
        """Create empty result for empty input."""
        return GeneralCSResult(
            detected_languages=[],
            confidence=0.0,
            probabilities={},
            word_analyses=[],
            switch_points=[],
            method="general-cs-empty",
            is_code_mixed=False,
            quality_metrics={},
            debug_info={}
        )
    
    def export_analysis(self, result: GeneralCSResult, include_debug: bool = True) -> Dict[str, Any]:
        """Export rich analysis for observability and refinement."""
        export_data = {
            "detection_result": {
                "detected_languages": result.detected_languages,
                "confidence": result.confidence,
                "probabilities": result.probabilities,
                "is_code_mixed": result.is_code_mixed,
                "method": result.method
            },
            "switch_analysis": {
                "switch_points": result.switch_points,
                "switch_count": len(result.switch_points)
            },
            "quality_metrics": result.quality_metrics
        }
        
        if include_debug:
            export_data["debug_info"] = result.debug_info
            export_data["word_analyses"] = [asdict(wa) for wa in result.word_analyses]
        
        return export_data

def main():
    """Test the general code-switching detector with different modes."""
    print("🌍 Testing General Code-Switching Detector")
    print("=" * 50)
    
    # Test different detector modes
    test_texts = [
        ("This is completely English text", "monolingual"),
        ("Hello amigo, comment allez-vous?", "code_switching"),
        ("Je parle français et español también", "multilingual")
    ]
    
    detector_modes = ["monolingual", "multilingual", "code_switching"]
    
    print("\n🎯 DETECTOR MODE COMPARISON:")
    print("=" * 50)
    
    for text, expected_type in test_texts:
        print(f"\n📝 Text ({expected_type}): \"{text}\"")
        print("-" * 40)
        
        for mode in detector_modes:
            detector = GeneralCodeSwitchingDetector(
                detector_mode=mode, 
                performance_mode="fast"  # Use fast mode for quick testing
            )
            
            import time
            start_time = time.time()
            result = detector.detect_language(text)
            end_time = time.time()
            
            print(f"{mode:>15}: {result.detected_languages} ({result.confidence:.2f}) - {(end_time-start_time)*1000:.1f}ms")
    
    print("\n" + "=" * 50)
    print("✅ Detector configuration complete!")
    print("🔍 Use 'monolingual' mode for single language detection")
    print("🌍 Use 'multilingual' mode for general multilingual text")
    print("🔄 Use 'code_switching' mode for code-switching detection")

if __name__ == "__main__":
    main()