#!/usr/bin/env python3
"""FastText-based language detection with enhanced accuracy."""

import fasttext
import os
import warnings
import re
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
from urllib.request import urlretrieve

from .language_detector import LanguageDetector, DetectionResult

warnings.filterwarnings("ignore", category=UserWarning, module="fasttext")


class FastTextDetector(LanguageDetector):
    """Enhanced language detector using Facebook's FastText library."""
    
    def __init__(self, model_path: Optional[str] = None, cache_size: int = 10000):
        """Initialize FastText detector.
        
        Args:
            model_path: Path to FastText model file. If None, downloads the default model.
            cache_size: Size of LRU cache for detection results.
        """
        super().__init__()
        self.model_path = model_path
        self.model = None
        self.cache_size = cache_size
        self.detector_type = "fasttext"  # Add detector type attribute
        self.buffer_size = 10  # Add buffer_size for streaming compatibility
        self.overlap_ratio = 0.2  # Add overlap_ratio for streaming compatibility
        self._load_model()
        
        # Enhanced language code mapping
        self.lang_code_mapping = {
            '__label__en': 'en', '__label__es': 'es', '__label__fr': 'fr',
            '__label__de': 'de', '__label__it': 'it', '__label__pt': 'pt',
            '__label__ru': 'ru', '__label__zh': 'zh', '__label__ja': 'ja',
            '__label__ko': 'ko', '__label__ar': 'ar', '__label__hi': 'hi',
            '__label__ur': 'ur', '__label__fa': 'fa', '__label__tr': 'tr',
            '__label__nl': 'nl', '__label__pl': 'pl', '__label__sv': 'sv',
            '__label__da': 'da', '__label__no': 'no', '__label__fi': 'fi',
            '__label__el': 'el', '__label__he': 'he', '__label__th': 'th',
            '__label__vi': 'vi', '__label__id': 'id', '__label__ms': 'ms',
            '__label__tl': 'tl', '__label__ta': 'ta', '__label__te': 'te',
            '__label__bn': 'bn', '__label__gu': 'gu', '__label__kn': 'kn',
            '__label__ml': 'ml', '__label__mr': 'mr', '__label__pa': 'pa',
            '__label__or': 'or', '__label__as': 'as', '__label__my': 'my',
            '__label__km': 'km', '__label__lo': 'lo', '__label__ka': 'ka',
            '__label__am': 'am', '__label__sw': 'sw', '__label__zu': 'zu',
            '__label__af': 'af', '__label__sq': 'sq', '__label__eu': 'eu',
            '__label__be': 'be', '__label__bg': 'bg', '__label__ca': 'ca',
            '__label__hr': 'hr', '__label__cs': 'cs', '__label__et': 'et',
            '__label__gl': 'gl', '__label__hu': 'hu', '__label__is': 'is',
            '__label__ga': 'ga', '__label__lv': 'lv', '__label__lt': 'lt',
            '__label__mk': 'mk', '__label__mt': 'mt', '__label__ro': 'ro',
            '__label__sk': 'sk', '__label__sl': 'sl', '__label__uk': 'uk',
            '__label__cy': 'cy', '__label__eo': 'eo', '__label__la': 'la'
        }
        
        # Preprocessing patterns for better accuracy
        self.preprocessing_patterns = [
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ''),
            (r'@[A-Za-z0-9_]+', ''),
            (r'#[A-Za-z0-9_]+', ''),
            (r'[0-9]+', ''),
            (r'[^\w\s]', ' '),
            (r'\s+', ' ')
        ]
    
    def _load_model(self):
        """Load FastText language identification model."""
        if self.model_path is None:
            self.model_path = self._download_default_model()
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"FastText model not found at {self.model_path}")
        
        try:
            self.model = fasttext.load_model(self.model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load FastText model: {e}")
    
    def _download_default_model(self) -> str:
        """Download the default FastText language identification model."""
        model_dir = os.path.join(os.path.expanduser("~"), ".fasttext")
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "lid.176.bin")
        
        if not os.path.exists(model_path):
            print("Downloading FastText language identification model...")
            url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
            urlretrieve(url, model_path)
            print(f"Model downloaded to {model_path}")
        
        return model_path
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better language detection."""
        if not text.strip():
            return ""
        
        # Don't lowercase - FastText is case-sensitive and capitalization is important for detection
        processed = text
        
        for pattern, replacement in self.preprocessing_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        return processed.strip()
    
    @lru_cache(maxsize=10000)
    def _detect_single_cached(self, text: str, k: int = 5) -> Tuple[List[str], List[float]]:
        """Cached single text detection."""
        if not text.strip():
            return ([], [])
        
        preprocessed = self._preprocess_text(text)
        if not preprocessed:
            return ([], [])
        
        try:
            predictions = self.model.predict(preprocessed, k=k)
            labels, scores = predictions
            
            # Convert tuple of labels to list and clean them
            clean_labels = []
            for label in labels:
                clean_label = self.lang_code_mapping.get(label, label.replace('__label__', ''))
                clean_labels.append(clean_label)
            
            # Convert numpy array to list
            scores_list = [float(score) for score in scores]
            
            return (clean_labels, scores_list)
        
        except Exception as e:
            print(f"FastText prediction error: {e}")
            return ([], [])
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> DetectionResult:
        """Detect language using FastText with code-mixing support."""
        if not text.strip():
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method='fasttext'
            )
        
        # Check for code-mixing using token-level analysis
        token_analysis = self._analyze_tokens(text)
        if token_analysis['is_code_mixed']:
            return self._handle_code_mixed_text(text, token_analysis, user_languages)
        
        # Standard single-language detection
        labels, scores = self._detect_single_cached(text)
        
        if not labels:
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method='fasttext'
            )
        
        probabilities = dict(zip(labels, scores))
        primary_language = labels[0]
        primary_confidence = scores[0]
        
        # Apply user language guidance boost
        if user_languages:
            user_lang_codes = [self._normalize_language_code(lang) for lang in user_languages]
            if primary_language in user_lang_codes:
                primary_confidence = min(1.0, primary_confidence * 1.15)
        
        # Check for secondary languages using confidence thresholds
        detected_languages = [primary_language]
        multilingual_threshold = 0.15  # Languages above this threshold are included
        
        for i, (lang, score) in enumerate(zip(labels[1:3], scores[1:3]), 1):
            if score > multilingual_threshold and lang != primary_language:
                detected_languages.append(lang)
        
        return DetectionResult(
            detected_languages=detected_languages,
            confidence=float(primary_confidence),
            probabilities=probabilities,
            method='fasttext'
        )
    
    def detect_languages_batch(self, texts: List[str], user_languages: Optional[List[str]] = None) -> List[DetectionResult]:
        """Batch detection for multiple texts."""
        return [self.detect_language(text, user_languages) for text in texts]
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(set(self.lang_code_mapping.values()))
    
    def _normalize_language_code(self, language: str) -> str:
        """Normalize language code to ISO 639-1 format."""
        language = language.lower().strip()
        
        normalization_map = {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh',
            'japanese': 'ja', 'korean': 'ko', 'arabic': 'ar', 'hindi': 'hi',
            'urdu': 'ur', 'persian': 'fa', 'farsi': 'fa', 'turkish': 'tr',
            'dutch': 'nl', 'polish': 'pl', 'swedish': 'sv', 'danish': 'da',
            'norwegian': 'no', 'finnish': 'fi', 'greek': 'el', 'hebrew': 'he',
            'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id', 'malay': 'ms',
            'tagalog': 'tl', 'filipino': 'tl', 'tamil': 'ta', 'telugu': 'te',
            'bengali': 'bn', 'gujarati': 'gu', 'kannada': 'kn', 'malayalam': 'ml',
            'marathi': 'mr', 'punjabi': 'pa', 'odia': 'or', 'assamese': 'as',
            'burmese': 'my', 'khmer': 'km', 'lao': 'lo', 'georgian': 'ka',
            'amharic': 'am', 'swahili': 'sw', 'zulu': 'zu', 'afrikaans': 'af'
        }
        
        return normalization_map.get(language, language)
    
    def _analyze_tokens(self, text: str) -> Dict:
        """Analyze text at token level for code-mixing detection."""
        tokens = text.split()
        if len(tokens) < 2:
            return {'is_code_mixed': False, 'token_languages': [], 'switch_points': []}
        
        # Romanization patterns for common code-mixed languages (very specific)
        romanization_patterns = {
            'hindi': ['aaj', 'kal', 'main', 'yaar', 'hoon', 'gayi', 'gaya', 'kaisa', 'kaise', 'accha', 'acchi', 'raha', 'rahi'],
            'urdu': ['aap', 'kya'],
            'arabic': ['qad', 'lam', 'lan']
        }
        
        token_languages = []
        romanization_count = 0
        
        for token in tokens:
            # Clean token
            clean_token = re.sub(r'[^\w]', '', token.lower())
            if not clean_token:
                token_languages.append('unknown')
                continue
            
            # Check for romanization patterns
            token_lang = None
            for lang, patterns in romanization_patterns.items():
                if clean_token in patterns:
                    token_lang = lang
                    romanization_count += 1
                    break
            
            # If no romanization match, use FastText on individual token
            if not token_lang:
                try:
                    labels, scores = self._detect_single_cached(token, k=3)
                    # Higher confidence threshold to avoid false positives
                    if labels and scores[0] > 0.6:  # Increased from 0.3 to 0.6
                        token_lang = labels[0]
                    else:
                        token_lang = 'unknown'
                except:
                    token_lang = 'unknown'
            
            token_languages.append(token_lang)
        
        # Detect switch points and code-mixing
        switch_points = []
        unique_languages = set(lang for lang in token_languages if lang != 'unknown')
        
        for i in range(1, len(token_languages)):
            if (token_languages[i] != token_languages[i-1] and 
                token_languages[i] != 'unknown' and 
                token_languages[i-1] != 'unknown'):
                switch_points.append(i)
        
        # More conservative code-mixing detection
        detected_romanization = romanization_count >= 1  # At least 1 romanized token
        is_code_mixed = (
            (len(unique_languages) > 1 and len(switch_points) > 0) or  # Multiple languages AND switches
            (detected_romanization and len(unique_languages) > 0)      # Romanization detected
        )
        
        return {
            'is_code_mixed': is_code_mixed,
            'token_languages': token_languages,
            'switch_points': switch_points,
            'unique_languages': list(unique_languages),
            'romanization_detected': detected_romanization
        }
    
    def _handle_code_mixed_text(self, text: str, token_analysis: Dict, user_languages: Optional[List[str]] = None) -> DetectionResult:
        """Handle code-mixed text with specialized logic."""
        # Get overall text-level detection
        labels, scores = self._detect_single_cached(text)
        if not labels:
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method='fasttext'
            )
        
        probabilities = dict(zip(labels, scores))
        
        # Combine text-level and token-level languages
        detected_languages = []
        
        # Add primary text-level language
        primary_language = labels[0]
        primary_confidence = scores[0]
        detected_languages.append(primary_language)
        
        # Add languages from token analysis with estimated probabilities
        for lang in token_analysis['unique_languages']:
            # Normalize language codes
            normalized_lang = self._normalize_language_code(lang)
            if normalized_lang not in detected_languages and lang != 'unknown':
                detected_languages.append(normalized_lang)
                
                # Add to probabilities with estimated score based on token frequency
                if normalized_lang not in probabilities:
                    token_count = sum(1 for tl in token_analysis['token_languages'] if self._normalize_language_code(tl) == normalized_lang)
                    total_tokens = len(token_analysis['token_languages'])
                    estimated_prob = (token_count / total_tokens) * 0.5  # Scale down to be conservative
                    probabilities[normalized_lang] = estimated_prob
        
        # Apply user language guidance
        if user_languages:
            user_lang_codes = [self._normalize_language_code(lang) for lang in user_languages]
            # Boost confidence if user languages are detected
            for user_lang in user_lang_codes:
                if user_lang in detected_languages:
                    primary_confidence = min(1.0, primary_confidence * 1.1)
        
        # Adjust confidence for code-mixed text (generally lower confidence)
        if len(detected_languages) > 1:
            primary_confidence *= 0.8  # Reduce confidence for mixed text
        
        return DetectionResult(
            detected_languages=detected_languages,
            confidence=float(primary_confidence),
            probabilities=probabilities,
            method='fasttext_codemixed',
            switch_points=token_analysis.get('switch_points', []),
            token_languages=token_analysis.get('token_languages', [])
        )
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if not self.model:
            return {}
        
        return {
            'model_path': self.model_path,
            'supported_languages': len(self.get_supported_languages()),
            'model_type': 'fasttext',
            'version': fasttext.__version__ if hasattr(fasttext, '__version__') else 'unknown'
        }