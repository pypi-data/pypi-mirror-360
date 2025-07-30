#!/usr/bin/env python3
"""Hybrid ensemble detector with confidence-aware token-level fusion."""

import re
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

from .language_detector import LanguageDetector, DetectionResult
from .fasttext_detector import FastTextDetector
from .transformer_detector import TransformerDetector
from ..utils.thresholds import ThresholdConfig, DetectionMode


@dataclass
class TokenPrediction:
    """Token-level prediction from a detector."""
    token: str
    position: int
    language: str
    confidence: float
    detector: str


@dataclass
class DisagreementLog:
    """Log entry for model disagreements."""
    token: str
    position: int
    fasttext_pred: str
    fasttext_conf: float
    transformer_pred: str
    transformer_conf: float
    resolution: str
    reasoning: str


@dataclass
class HybridResult:
    """Result from hybrid ensemble detection."""
    detected_languages: List[str]
    confidence: float
    probabilities: Dict[str, float]
    token_predictions: List[TokenPrediction]
    switch_points: List[int]
    disagreement_log: List[DisagreementLog]
    method: str
    quality_metrics: Dict[str, Any]


class HybridEnsembleDetector(LanguageDetector):
    """
    Hybrid ensemble detector combining FastText and Transformer with confidence-aware fusion.
    
    Strategy:
    - Token-level analysis with both models
    - Confidence-aware weighted voting
    - FastText prioritized for romanized/noisy text
    - Transformer for ambiguous/context-rich sequences
    - Disagreement handling with confidence margins
    - Optional transformer for latency-sensitive apps
    """
    
    def __init__(self,
                 use_transformer: bool = True,
                 transformer_model: str = "papluca/xlm-roberta-base-language-detection",
                 confidence_margin: float = 0.15,
                 code_mixing_threshold: int = 2,
                 romanization_boost: float = 0.2,
                 context_window: int = 3,
                 enable_disagreement_logging: bool = True):
        """Initialize hybrid ensemble detector.
        
        Args:
            use_transformer: Enable transformer model (disable for latency-sensitive apps)
            transformer_model: Transformer model to use
            confidence_margin: Margin for disagreement resolution
            code_mixing_threshold: Min languages above margin for code-mixed classification
            romanization_boost: Confidence boost for FastText on romanized text
            context_window: Context window for transformer disambiguation
            enable_disagreement_logging: Log model disagreements for interpretability
        """
        super().__init__()
        
        self.use_transformer = use_transformer
        self.confidence_margin = confidence_margin
        self.code_mixing_threshold = code_mixing_threshold
        self.romanization_boost = romanization_boost
        self.context_window = context_window
        self.enable_disagreement_logging = enable_disagreement_logging
        
        # Initialize detectors
        self.fasttext = FastTextDetector()
        self.transformer = None
        
        if use_transformer:
            try:
                self.transformer = TransformerDetector(model_name=transformer_model)
                print(f"✓ Hybrid ensemble with transformer enabled")
            except Exception as e:
                print(f"⚠ Transformer failed to load, using FastText only: {e}")
                self.use_transformer = False
        else:
            print(f"✓ Hybrid ensemble (FastText only, latency-optimized)")
        
        # Romanization patterns for FastText prioritization
        self.romanization_patterns = {
            'hindi': ['aaj', 'kal', 'main', 'yaar', 'hoon', 'gayi', 'gaya', 'kaisa', 'kaise', 'accha', 'raha', 'rahi'],
            'urdu': ['aap', 'kya', 'kaise'],
            'arabic': ['wa', 'fi', 'min', 'ila']
        }
        
        self.disagreement_log = []
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> HybridResult:
        """Detect language using hybrid confidence-aware fusion."""
        if not text.strip():
            return HybridResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                token_predictions=[],
                switch_points=[],
                disagreement_log=[],
                method='hybrid-empty',
                quality_metrics={}
            )
        
        # Tokenize text
        tokens = self._tokenize_with_positions(text)
        
        # Get token-level predictions from both models
        token_predictions = self._get_token_predictions(tokens, text, user_languages)
        
        # Apply confidence-aware fusion
        fused_predictions = self._apply_confidence_fusion(token_predictions, text)
        
        # Aggregate to sentence level
        sentence_result = self._aggregate_to_sentence_level(fused_predictions, text)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(fused_predictions, text)
        
        return HybridResult(
            detected_languages=sentence_result['languages'],
            confidence=sentence_result['confidence'],
            probabilities=sentence_result['probabilities'],
            token_predictions=fused_predictions,
            switch_points=sentence_result['switch_points'],
            disagreement_log=self.disagreement_log,
            method=f"hybrid-{'transformer' if self.use_transformer else 'fasttext'}",
            quality_metrics=quality_metrics
        )
    
    def _tokenize_with_positions(self, text: str) -> List[Tuple[str, int]]:
        """Tokenize text while preserving positions."""
        tokens = []
        words = text.split()
        
        for i, word in enumerate(words):
            # Clean token for analysis
            clean_token = re.sub(r'[^\w]', '', word.lower())
            if clean_token:
                tokens.append((clean_token, i))
        
        return tokens
    
    def _get_token_predictions(self, tokens: List[Tuple[str, int]], 
                              full_text: str, user_languages: Optional[List[str]]) -> List[TokenPrediction]:
        """Get token-level predictions from both models."""
        predictions = []
        
        for token, position in tokens:
            # FastText prediction (always available)
            ft_pred = self._get_fasttext_token_prediction(token, position)
            
            # Transformer prediction (if available and beneficial)
            trans_pred = None
            if self.use_transformer and self._should_use_transformer(token, position, full_text):
                trans_pred = self._get_transformer_token_prediction(token, position, full_text)
            
            # Store predictions for fusion
            token_preds = {'fasttext': ft_pred}
            if trans_pred:
                token_preds['transformer'] = trans_pred
            
            predictions.append(token_preds)
        
        return predictions
    
    def _get_fasttext_token_prediction(self, token: str, position: int) -> TokenPrediction:
        """Get FastText prediction for a single token."""
        try:
            result = self.fasttext.detect_language(token)
            
            # Check for romanization patterns
            is_romanized = self._is_romanized_token(token)
            confidence = result.confidence
            
            if is_romanized:
                # Boost confidence for romanized tokens
                confidence = min(1.0, confidence + self.romanization_boost)
            
            language = result.detected_languages[0] if result.detected_languages else 'unknown'
            
            return TokenPrediction(
                token=token,
                position=position,
                language=language,
                confidence=confidence,
                detector='fasttext'
            )
        except Exception:
            return TokenPrediction(
                token=token,
                position=position,
                language='unknown',
                confidence=0.0,
                detector='fasttext'
            )
    
    def _get_transformer_token_prediction(self, token: str, position: int, 
                                        full_text: str) -> TokenPrediction:
        """Get Transformer prediction with context."""
        try:
            # Create context window around token
            words = full_text.split()
            start_idx = max(0, position - self.context_window)
            end_idx = min(len(words), position + self.context_window + 1)
            context = ' '.join(words[start_idx:end_idx])
            
            result = self.transformer.detect_language(context)
            language = result.detected_languages[0] if result.detected_languages else 'unknown'
            
            return TokenPrediction(
                token=token,
                position=position,
                language=language,
                confidence=result.confidence,
                detector='transformer'
            )
        except Exception:
            return TokenPrediction(
                token=token,
                position=position,
                language='unknown',
                confidence=0.0,
                detector='transformer'
            )
    
    def _should_use_transformer(self, token: str, position: int, full_text: str) -> bool:
        """Determine if transformer should be used for this token."""
        # Use transformer for:
        # 1. Short ambiguous tokens
        # 2. Tokens that might need context
        # 3. Non-romanized tokens where FastText might struggle
        
        if len(token) <= 2:
            return True  # Short tokens need context
        
        if not self._is_romanized_token(token):
            return True  # Non-romanized tokens benefit from transformer
        
        # Use transformer for every Nth token to maintain coverage
        return position % 3 == 0
    
    def _is_romanized_token(self, token: str) -> bool:
        """Check if token appears to be romanized."""
        token_lower = token.lower()
        
        for lang, patterns in self.romanization_patterns.items():
            if token_lower in patterns:
                return True
        
        return False
    
    def _apply_confidence_fusion(self, token_predictions: List[Dict], full_text: str) -> List[TokenPrediction]:
        """Apply confidence-aware fusion to resolve disagreements."""
        fused_predictions = []
        
        for i, token_preds in enumerate(token_predictions):
            ft_pred = token_preds['fasttext']
            trans_pred = token_preds.get('transformer')
            
            if not trans_pred:
                # Only FastText available
                fused_predictions.append(ft_pred)
                continue
            
            # Both predictions available - apply fusion logic
            fused_pred = self._resolve_disagreement(ft_pred, trans_pred, full_text)
            fused_predictions.append(fused_pred)
        
        return fused_predictions
    
    def _resolve_disagreement(self, ft_pred: TokenPrediction, 
                            trans_pred: TokenPrediction, full_text: str) -> TokenPrediction:
        """Resolve disagreements between FastText and Transformer."""
        token = ft_pred.token
        position = ft_pred.position
        
        # No disagreement
        if ft_pred.language == trans_pred.language:
            # Use higher confidence
            if ft_pred.confidence >= trans_pred.confidence:
                return ft_pred
            else:
                return trans_pred
        
        # Disagreement exists - apply resolution strategy
        confidence_diff = abs(ft_pred.confidence - trans_pred.confidence)
        is_romanized = self._is_romanized_token(token)
        
        # Resolution logic
        resolution = None
        reasoning = ""
        
        if is_romanized and ft_pred.confidence > 0.5:
            # FastText prioritized for romanized tokens
            resolution = ft_pred
            reasoning = "FastText prioritized for romanized token"
        elif confidence_diff > self.confidence_margin:
            # High confidence difference - use more confident model
            if ft_pred.confidence > trans_pred.confidence:
                resolution = ft_pred
                reasoning = f"FastText higher confidence ({ft_pred.confidence:.3f} vs {trans_pred.confidence:.3f})"
            else:
                resolution = trans_pred
                reasoning = f"Transformer higher confidence ({trans_pred.confidence:.3f} vs {ft_pred.confidence:.3f})"
        elif trans_pred.confidence > 0.7:
            # Transformer highly confident
            resolution = trans_pred
            reasoning = "Transformer high confidence for disambiguation"
        else:
            # Default to FastText for consistency
            resolution = ft_pred
            reasoning = "Default to FastText for consistency"
        
        # Log disagreement
        if self.enable_disagreement_logging:
            self.disagreement_log.append(DisagreementLog(
                token=token,
                position=position,
                fasttext_pred=ft_pred.language,
                fasttext_conf=ft_pred.confidence,
                transformer_pred=trans_pred.language,
                transformer_conf=trans_pred.confidence,
                resolution=resolution.language,
                reasoning=reasoning
            ))
        
        return resolution
    
    def _aggregate_to_sentence_level(self, token_predictions: List[TokenPrediction], 
                                   text: str) -> Dict[str, Any]:
        """Aggregate token-level predictions to sentence level."""
        if not token_predictions:
            return {
                'languages': [],
                'confidence': 0.0,
                'probabilities': {},
                'switch_points': []
            }
        
        # Count language occurrences with confidence weighting
        language_scores = defaultdict(float)
        total_confidence = 0.0
        
        for pred in token_predictions:
            if pred.language != 'unknown':
                language_scores[pred.language] += pred.confidence
                total_confidence += pred.confidence
        
        # Normalize to probabilities
        probabilities = {}
        if total_confidence > 0:
            for lang, score in language_scores.items():
                probabilities[lang] = score / total_confidence
        
        # Determine detected languages (above threshold)
        detected_languages = []
        for lang, prob in probabilities.items():
            if prob >= (1.0 / self.code_mixing_threshold):  # Dynamic threshold
                detected_languages.append(lang)
        
        # Sort by probability
        detected_languages.sort(key=lambda l: probabilities[l], reverse=True)
        
        # Ensure at least one language if we have predictions
        if not detected_languages and probabilities:
            detected_languages = [max(probabilities.keys(), key=lambda l: probabilities[l])]
        
        # Find switch points
        switch_points = []
        prev_lang = None
        for i, pred in enumerate(token_predictions):
            if prev_lang and pred.language != prev_lang and pred.language != 'unknown':
                switch_points.append(i)
            if pred.language != 'unknown':
                prev_lang = pred.language
        
        # Calculate overall confidence
        if detected_languages:
            overall_confidence = max(probabilities[lang] for lang in detected_languages)
        else:
            overall_confidence = 0.0
        
        return {
            'languages': detected_languages,
            'confidence': overall_confidence,
            'probabilities': probabilities,
            'switch_points': switch_points
        }
    
    def _calculate_quality_metrics(self, token_predictions: List[TokenPrediction], 
                                 text: str) -> Dict[str, Any]:
        """Calculate quality metrics for interpretability."""
        if not token_predictions:
            return {}
        
        # Model usage statistics
        fasttext_count = sum(1 for p in token_predictions if p.detector == 'fasttext')
        transformer_count = sum(1 for p in token_predictions if p.detector == 'transformer')
        
        # Confidence statistics
        confidences = [p.confidence for p in token_predictions if p.confidence > 0]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        min_confidence = min(confidences) if confidences else 0.0
        max_confidence = max(confidences) if confidences else 0.0
        
        # Language diversity
        unique_languages = len(set(p.language for p in token_predictions if p.language != 'unknown'))
        
        # Romanization detection
        romanized_tokens = sum(1 for p in token_predictions if self._is_romanized_token(p.token))
        
        return {
            'total_tokens': len(token_predictions),
            'fasttext_usage': fasttext_count,
            'transformer_usage': transformer_count,
            'avg_confidence': avg_confidence,
            'min_confidence': min_confidence,
            'max_confidence': max_confidence,
            'unique_languages': unique_languages,
            'romanized_tokens': romanized_tokens,
            'disagreements': len(self.disagreement_log),
            'switch_points_detected': len(set(p.language for p in token_predictions if p.language != 'unknown')) > 1
        }
    
    def get_disagreement_summary(self) -> Dict[str, Any]:
        """Get summary of model disagreements for analysis."""
        if not self.disagreement_log:
            return {'total_disagreements': 0}
        
        # Analyze disagreement patterns
        resolution_counts = defaultdict(int)
        language_pairs = defaultdict(int)
        
        for log in self.disagreement_log:
            resolution_counts[log.resolution] += 1
            pair = tuple(sorted([log.fasttext_pred, log.transformer_pred]))
            language_pairs[pair] += 1
        
        return {
            'total_disagreements': len(self.disagreement_log),
            'resolution_distribution': dict(resolution_counts),
            'common_disagreement_pairs': dict(language_pairs),
            'avg_fasttext_confidence': np.mean([log.fasttext_conf for log in self.disagreement_log]),
            'avg_transformer_confidence': np.mean([log.transformer_conf for log in self.disagreement_log])
        }
    
    def clear_disagreement_log(self):
        """Clear disagreement log for new analysis."""
        self.disagreement_log = []


def main():
    """Example usage of hybrid ensemble detector."""
    # Test with transformer enabled (research/accuracy mode)
    print("🔬 Testing Hybrid Ensemble (Research Mode)")
    detector_research = HybridEnsembleDetector(use_transformer=True)
    
    test_cases = [
        "Good morning! Aaj ka weather kaisa hai?",
        "Main office ja raha hoon, will call you later",
        "Yaar, this movie is really accha!"
    ]
    
    for text in test_cases:
        result = detector_research.detect_language(text)
        print(f"\nText: '{text}'")
        print(f"Languages: {result.detected_languages}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Switch points: {result.switch_points}")
        print(f"Disagreements: {len(result.disagreement_log)}")
        print(f"Quality: {result.quality_metrics}")
    
    # Test latency-optimized mode
    print("\n⚡ Testing Hybrid Ensemble (Latency Mode)")
    detector_fast = HybridEnsembleDetector(use_transformer=False)
    
    result_fast = detector_fast.detect_language(test_cases[0])
    print(f"Fast mode result: {result_fast.detected_languages}")


if __name__ == "__main__":
    main()