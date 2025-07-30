"""Language detection for multilingual text."""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from langdetect import detect, detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException


@dataclass
class DetectionResult:
    """Result from language detection."""
    detected_languages: List[str]
    confidence: float
    probabilities: Dict[str, float]
    method: str = "langdetect"
    switch_points: Optional[List[int]] = None
    token_languages: Optional[List[str]] = None


class LanguageDetector:
    """Detects languages in text with support for multilingual content."""
    
    def __init__(self, seed: int = 0):
        """Initialize the language detector.
        
        Args:
            seed: Random seed for consistent results.
        """
        DetectorFactory.seed = seed
        self.confidence_threshold = 0.7
        self.minimum_text_length = 3
        
    def detect_primary_language(self, text: str) -> Optional[str]:
        """Detect the primary language of the text.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Language code (e.g., 'en', 'es') or None if detection fails.
        """
        if not self._is_valid_text(text):
            return None
            
        try:
            return detect(text)
        except LangDetectException:
            return None
    
    def detect_languages_with_confidence(self, text: str) -> List[Dict[str, float]]:
        """Detect all languages in text with confidence scores.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            List of dicts with 'language' and 'confidence' keys.
        """
        if not self._is_valid_text(text):
            return []
            
        try:
            lang_probs = detect_langs(text)
            return [
                {"language": lang.lang, "confidence": lang.prob}
                for lang in lang_probs
                if lang.prob >= self.confidence_threshold
            ]
        except LangDetectException:
            return []
    
    def detect_sentence_languages(self, text: str) -> List[Dict[str, str]]:
        """Detect language for each sentence in the text.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            List of dicts with 'sentence' and 'language' keys.
        """
        sentences = self._split_into_sentences(text)
        results = []
        
        for sentence in sentences:
            language = self.detect_primary_language(sentence)
            results.append({
                "sentence": sentence.strip(),
                "language": language or "unknown"
            })
        
        return results
    
    def is_multilingual(self, text: str, min_languages: int = 2) -> bool:
        """Check if text contains multiple languages.
        
        Args:
            text: Input text to analyze.
            min_languages: Minimum number of languages to consider multilingual.
            
        Returns:
            True if text is multilingual, False otherwise.
        """
        languages = self.detect_languages_with_confidence(text)
        return len(languages) >= min_languages
    
    def get_language_distribution(self, text: str) -> Dict[str, float]:
        """Get the distribution of languages in the text.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Dict mapping language codes to normalized confidence scores.
        """
        languages = self.detect_languages_with_confidence(text)
        if not languages:
            return {}
        
        total_confidence = sum(lang["confidence"] for lang in languages)
        return {
            lang["language"]: lang["confidence"] / total_confidence
            for lang in languages
        }
    
    def _is_valid_text(self, text: str) -> bool:
        """Check if text is valid for language detection.
        
        Args:
            text: Text to validate.
            
        Returns:
            True if text is valid, False otherwise.
        """
        if not text or not isinstance(text, str):
            return False
        
        cleaned_text = re.sub(r'[^\w\s]', '', text).strip()
        return len(cleaned_text) >= self.minimum_text_length
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> DetectionResult:
        """Detect language using langdetect with standardized interface.
        
        Args:
            text: Input text to analyze.
            user_languages: Optional list of user languages (not used in base detector).
            
        Returns:
            DetectionResult object with detected languages and confidence.
        """
        if not self._is_valid_text(text):
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method="langdetect"
            )
        
        try:
            # Get primary language
            primary_lang = detect(text)
            
            # Get all languages with confidence
            lang_probs = detect_langs(text)
            probabilities = {lang.lang: lang.prob for lang in lang_probs}
            
            # Get confidence for primary language
            confidence = probabilities.get(primary_lang, 0.0)
            
            return DetectionResult(
                detected_languages=[primary_lang],
                confidence=confidence,
                probabilities=probabilities,
                method="langdetect"
            )
            
        except LangDetectException:
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method="langdetect"
            )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple rules.
        
        Args:
            text: Text to split.
            
        Returns:
            List of sentences.
        """
        sentence_endings = re.compile(r'[.!?]+')
        sentences = sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]