#!/usr/bin/env python3
"""
Detector Improvements Based on Error Analysis

Implements targeted fixes for the major issues identified:
1. Language count mismatch (22 cases) - Over-detection of languages
2. False negative CS (12 cases) - Missing code-switching
3. Wrong language identification (10 cases) - Incorrect language mapping
4. Poor confidence calibration - High confidence on wrong predictions
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

from ..detection.general_cs_detector import GeneralCodeSwitchingDetector, GeneralCSResult
from ..utils.thresholds import ThresholdConfig, DetectionMode


class ImprovedGeneralCSDetector(GeneralCodeSwitchingDetector):
    """Enhanced GeneralCS detector with targeted improvements from error analysis."""
    
    def __init__(self, *args, **kwargs):
        """Initialize with improvements."""
        super().__init__(*args, **kwargs)
        
        # Enhanced language filtering
        self.improved_language_filtering = True
        self.romanized_language_patterns = self._load_romanized_patterns()
        self.common_loanwords = self._load_common_loanwords()
        
        # Improved thresholds based on error analysis
        self.enhanced_thresholds = {
            'min_language_confidence': 0.4,  # Increased from 0.3
            'min_switch_confidence': 0.5,    # Higher bar for switches
            'max_languages_per_text': 3,     # Limit over-detection
            'romanized_boost': 0.15          # Boost for romanized text
        }
        
        # Language-specific adjustments
        self.language_adjustments = {
            'ar': {'boost': 0.2, 'romanized_keywords': ['yallah', 'habibi', 'inshallah']},
            'hi': {'boost': 0.15, 'romanized_keywords': ['chai', 'bhai', 'yaar', 'aaj', 'kal', 'jaldi']},
            'es': {'boost': 0.1, 'romanized_keywords': ['hola', 'gracias', 'vamos', 'amigo']},
            'de': {'boost': 0.1, 'romanized_keywords': ['guten', 'danke', 'sehr', 'gut']},
        }
        
        print(f"✨ Initialized Improved GeneralCS detector with error analysis fixes")
    
    def _load_romanized_patterns(self) -> Dict[str, List[str]]:
        """Load romanized language patterns for better detection."""
        return {
            'hi': [
                r'\b(aaj|kal|jaldi|bhai|yaar|kya|hai|hain|pe|ke|ka|ki|ko|se|me|main|mujhe|tumhe|wo|ye)\b',
                r'\b(chalein?|milte|samajh|nahi|pata|lagta|bata|scene|chill|full)\b',
                r'\b(abbu|mama|ghar|college|test|cancel|hua|kya|toh|sirf|bolti)\b'
            ],
            'ar': [
                r'\b(yallah|habibi|inshallah|mashallah|maghrib)\b',
                r'\b(wallah|khalas|mabrook|shukran)\b'
            ],
            'es': [
                r'\b(hola|gracias|por favor|vamos|amigo|niña|mamá|café)\b',
                r'\b(mercado|playa|biblioteca|problema|examen)\b'
            ],
            'de': [
                r'\b(guten|danke|sehr|gut|tag|nacht)\b',
                r'\b(schön|bitte|entschuldigung)\b'
            ]
        }
    
    def _load_common_loanwords(self) -> Dict[str, str]:
        """Load common loanwords that are often misclassified."""
        return {
            # Hindi/Urdu loanwords in English
            'chai': 'hi', 'bhai': 'hi', 'yaar': 'hi', 'desi': 'hi',
            'guru': 'hi', 'karma': 'hi', 'yoga': 'hi', 'mantra': 'hi',
            
            # Spanish loanwords in English
            'fiesta': 'es', 'siesta': 'es', 'patio': 'es', 'plaza': 'es',
            'amigo': 'es', 'gracias': 'es', 'hola': 'es',
            
            # French loanwords in English
            'café': 'fr', 'cuisine': 'fr', 'résumé': 'fr', 'rendezvous': 'fr',
            'boutique': 'fr', 'entrepreneur': 'fr',
            
            # Arabic loanwords
            'yallah': 'ar', 'habibi': 'ar', 'inshallah': 'ar', 'mashallah': 'ar'
        }
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> GeneralCSResult:
        """Enhanced detection with targeted improvements."""
        
        # Get base result
        base_result = super().detect_language(text, user_languages)
        
        # Apply improvements
        improved_result = self._apply_improvements(text, base_result, user_languages)
        
        return improved_result
    
    def _apply_improvements(self, text: str, base_result: GeneralCSResult, 
                          user_languages: Optional[List[str]]) -> GeneralCSResult:
        """Apply targeted improvements based on error analysis."""
        
        # 1. Fix language count mismatch (major issue)
        filtered_languages = self._filter_excessive_languages(
            text, base_result.detected_languages, base_result.probabilities
        )
        
        # 2. Enhance romanized text detection
        romanized_boost = self._apply_romanized_boost(text, filtered_languages)
        
        # 3. Fix wrong language identification with loanword detection
        corrected_languages = self._correct_language_identification(
            text, romanized_boost
        )
        
        # 4. Improve confidence calibration
        calibrated_confidence = self._calibrate_confidence(
            text, corrected_languages, base_result.confidence
        )
        
        # 5. Enhanced switch detection
        improved_switches = self._improve_switch_detection(
            text, corrected_languages, base_result.switch_points
        )
        
        # Create improved result
        improved_result = GeneralCSResult(
            detected_languages=corrected_languages,
            confidence=calibrated_confidence,
            probabilities=self._recalculate_probabilities(corrected_languages, calibrated_confidence),
            word_analyses=base_result.word_analyses,  # Keep original for now
            switch_points=improved_switches,
            method="improved_general_cs",
            is_code_mixed=len(corrected_languages) > 1,
            quality_metrics=self._calculate_improved_quality_metrics(text, corrected_languages),
            debug_info={
                **base_result.debug_info,
                'improvements_applied': True,
                'original_languages': base_result.detected_languages,
                'original_confidence': base_result.confidence
            }
        )
        
        return improved_result
    
    def _filter_excessive_languages(self, text: str, languages: List[str], 
                                   probabilities: Dict[str, float]) -> List[str]:
        """Fix language count mismatch by filtering excessive language detection."""
        
        # If only 1-2 languages detected, likely correct
        if len(languages) <= 2:
            return languages
        
        # For longer lists, keep only high-confidence languages
        high_conf_languages = []
        sorted_langs = sorted(languages, key=lambda l: probabilities.get(l, 0), reverse=True)
        
        for lang in sorted_langs[:self.enhanced_thresholds['max_languages_per_text']]:
            lang_conf = probabilities.get(lang, 0)
            if lang_conf >= self.enhanced_thresholds['min_language_confidence']:
                high_conf_languages.append(lang)
        
        # Ensure at least one language
        if not high_conf_languages and sorted_langs:
            high_conf_languages = [sorted_langs[0]]
        
        return high_conf_languages
    
    def _apply_romanized_boost(self, text: str, languages: List[str]) -> List[str]:
        """Boost detection for romanized text patterns."""
        
        text_lower = text.lower()
        detected_romanized = set()
        
        # Check for romanized patterns
        for lang, patterns in self.romanized_language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected_romanized.add(lang)
        
        # Boost detected romanized languages
        boosted_languages = list(languages)
        for lang in detected_romanized:
            if lang not in boosted_languages:
                # Check if we should add this language
                words = text_lower.split()
                romanized_words = 0
                for word in words:
                    if any(re.search(pattern, word) for pattern in self.romanized_language_patterns[lang]):
                        romanized_words += 1
                
                # Add if significant romanized content
                if romanized_words >= 1 and len(words) <= 6:  # Short text with romanized
                    boosted_languages.append(lang)
                elif romanized_words >= 2:  # Longer text with multiple romanized words
                    boosted_languages.append(lang)
        
        return boosted_languages
    
    def _correct_language_identification(self, text: str, languages: List[str]) -> List[str]:
        """Correct wrong language identification using loanword detection."""
        
        words = text.lower().split()
        corrected_languages = list(languages)
        
        # Check for loanwords
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.common_loanwords:
                correct_lang = self.common_loanwords[clean_word]
                if correct_lang not in corrected_languages:
                    corrected_languages.append(correct_lang)
        
        # Remove unlikely languages for short text
        if len(words) <= 3:
            # For very short text, be conservative
            high_confidence_langs = []
            for lang in corrected_languages:
                # Keep if it's English (most common) or if we found specific markers
                if lang == 'en':
                    high_confidence_langs.append(lang)
                elif any(word in self.common_loanwords and self.common_loanwords[word] == lang 
                        for word in words):
                    high_confidence_langs.append(lang)
                elif lang in self.language_adjustments:
                    # Check for romanized keywords
                    keywords = self.language_adjustments[lang].get('romanized_keywords', [])
                    if any(keyword in text.lower() for keyword in keywords):
                        high_confidence_langs.append(lang)
            
            if high_confidence_langs:
                corrected_languages = high_confidence_langs
        
        return corrected_languages[:self.enhanced_thresholds['max_languages_per_text']]
    
    def _calibrate_confidence(self, text: str, languages: List[str], 
                            original_confidence: float) -> float:
        """Improve confidence calibration based on error analysis findings."""
        
        text_length = len(text.split())
        
        # Base confidence adjustment
        adjusted_confidence = original_confidence
        
        # Reduce confidence for problematic cases identified in error analysis
        if len(languages) > 2:
            # Multi-language detection is often wrong
            adjusted_confidence *= 0.7
        
        if text_length <= 3:
            # Very short text is unreliable
            adjusted_confidence *= 0.8
        
        # Boost confidence for clear indicators
        text_lower = text.lower()
        clear_indicators = 0
        
        # Count clear language indicators
        for lang in languages:
            if lang in self.language_adjustments:
                keywords = self.language_adjustments[lang].get('romanized_keywords', [])
                for keyword in keywords:
                    if keyword in text_lower:
                        clear_indicators += 1
        
        # Boost confidence if we have clear indicators
        if clear_indicators >= 1:
            adjusted_confidence = min(1.0, adjusted_confidence * 1.2)
        
        # Ensure confidence stays in reasonable bounds
        adjusted_confidence = max(0.1, min(0.95, adjusted_confidence))
        
        return adjusted_confidence
    
    def _improve_switch_detection(self, text: str, languages: List[str], 
                                original_switches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Improve switch point detection based on error analysis."""
        
        # If monolingual, no switches
        if len(languages) <= 1:
            return []
        
        # For code-switching text, be more conservative about switch points
        words = text.split()
        improved_switches = []
        
        # Simple heuristic: look for clear language boundaries
        current_lang = languages[0] if languages else 'en'
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Check if this word strongly indicates a language switch
            likely_lang = None
            for lang in languages:
                if lang in self.language_adjustments:
                    keywords = self.language_adjustments[lang].get('romanized_keywords', [])
                    if word_lower in keywords:
                        likely_lang = lang
                        break
            
            # Check loanwords
            if word_lower in self.common_loanwords:
                likely_lang = self.common_loanwords[word_lower]
            
            # If we detected a switch
            if likely_lang and likely_lang != current_lang and likely_lang in languages:
                improved_switches.append({
                    'position': i,
                    'from_language': current_lang,
                    'to_language': likely_lang,
                    'confidence': 0.8,
                    'method': 'improved_heuristic'
                })
                current_lang = likely_lang
        
        return improved_switches
    
    def _recalculate_probabilities(self, languages: List[str], 
                                 confidence: float) -> Dict[str, float]:
        """Recalculate probabilities for corrected languages."""
        if not languages:
            return {}
        
        if len(languages) == 1:
            return {languages[0]: confidence}
        
        # Distribute confidence among detected languages
        base_prob = confidence / len(languages)
        probabilities = {}
        
        for i, lang in enumerate(languages):
            # Give slight preference to first language
            prob = base_prob * (1.2 if i == 0 else 0.9)
            probabilities[lang] = min(1.0, prob)
        
        return probabilities
    
    def _calculate_improved_quality_metrics(self, text: str, 
                                          languages: List[str]) -> Dict[str, Any]:
        """Calculate quality metrics for improved detection."""
        return {
            'text_length': len(text.split()),
            'language_count': len(languages),
            'has_romanized': any(
                re.search(pattern, text.lower())
                for patterns in self.romanized_language_patterns.values()
                for pattern in patterns
            ),
            'improvement_applied': True,
            'confidence_source': 'calibrated'
        }


def test_improvements():
    """Test the improvements on problematic cases."""
    
    print("🧪 TESTING DETECTOR IMPROVEMENTS")
    print("=" * 50)
    
    # Create both detectors for comparison
    original = GeneralCodeSwitchingDetector(performance_mode="accurate")
    improved = ImprovedGeneralCSDetector(performance_mode="accurate")
    
    # Test cases that were problematic
    test_cases = [
        "Yallah chalein",  # Arabic-Hindi
        "Bhai pls",        # Hindi-English
        "I need chai right now",  # English-Hindi
        "Ok चलो",          # English-Hindi with script mixing
        "Mujhe lagta hai ke if we try hard, we can still submit",  # Long mixed
        "Hello world",     # Monolingual (should stay monolingual)
    ]
    
    for text in test_cases:
        print(f"\n📝 Text: \"{text}\"")
        
        # Original result
        orig_result = original.detect_language(text)
        print(f"  Original: {orig_result.detected_languages} (conf: {orig_result.confidence:.3f})")
        
        # Improved result
        imp_result = improved.detect_language(text)
        print(f"  Improved: {imp_result.detected_languages} (conf: {imp_result.confidence:.3f})")
        
        # Show improvement
        if len(imp_result.detected_languages) < len(orig_result.detected_languages):
            print("    ✅ Reduced over-detection")
        elif imp_result.confidence != orig_result.confidence:
            print("    📊 Adjusted confidence")


if __name__ == "__main__":
    test_improvements()