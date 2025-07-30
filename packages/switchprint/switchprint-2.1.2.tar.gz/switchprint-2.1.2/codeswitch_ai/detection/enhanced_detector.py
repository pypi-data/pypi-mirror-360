"""Enhanced code-switch detection based on user-guided analysis."""

import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import functools
import hashlib
from .language_detector import LanguageDetector


@dataclass
class PhraseCluster:
    """Represents a cluster of words in the same language."""
    words: List[str]
    text: str
    language: str
    confidence: float
    start_index: int
    end_index: int
    is_user_language: bool


@dataclass
class EnhancedDetectionResult:
    """Result from enhanced detection analysis."""
    tokens: List[Dict[str, any]]
    phrases: List[PhraseCluster]
    switch_points: List[int]
    confidence: float
    user_language_match: bool
    detected_languages: List[str]
    romanization_detected: bool


class SimpleCache:
    """Simple LRU cache for detection results."""
    
    def __init__(self, max_size: int = 500, ttl_minutes: int = 15):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self.access_times.items()
            if now - timestamp > self.ttl
        ]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)
    
    def _evict_lru(self):
        """Remove least recently used entry."""
        if not self.access_times:
            return
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.cache.pop(lru_key, None)
        self.access_times.pop(lru_key, None)
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value."""
        if len(self.cache) > self.max_size * 0.8:
            self._cleanup_expired()
        
        if key in self.cache:
            self.access_times[key] = datetime.now()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: any):
        """Set cached value."""
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = value
        self.access_times[key] = datetime.now()


class EnhancedCodeSwitchDetector:
    """Enhanced code-switching detector with user guidance and improved accuracy."""
    
    def __init__(self, base_detector: Optional[LanguageDetector] = None):
        """Initialize enhanced detector.
        
        Args:
            base_detector: Base language detector instance.
        """
        self.base_detector = base_detector or LanguageDetector()
        self.cache = SimpleCache()
        
        # Confidence thresholds
        self.default_confidence_threshold = 0.6
        self.user_language_confidence_threshold = 0.4
        self.romanized_confidence_threshold = 0.3
        
        # Context window settings
        self.context_windows = {
            'very_short': {'min_length': 1, 'max_length': 1, 'text_threshold': 5},
            'short': {'min_length': 2, 'max_length': 3, 'text_threshold': 15},
            'medium': {'min_length': 2, 'max_length': 4, 'text_threshold': 30},
            'long': {'min_length': 3, 'max_length': 5, 'text_threshold': float('inf')}
        }
        
        # Function word mappings for better accuracy
        self.function_words = {
            # English
            'the': 'en', 'and': 'en', 'or': 'en', 'but': 'en', 'is': 'en', 'are': 'en',
            'a': 'en', 'an': 'en', 'to': 'en', 'for': 'en', 'of': 'en', 'in': 'en',
            'i': 'en', 'you': 'en', 'he': 'en', 'she': 'en', 'it': 'en', 'we': 'en',
            'this': 'en', 'that': 'en', 'my': 'en', 'your': 'en', 'his': 'en', 'her': 'en',
            
            # Spanish
            'el': 'es', 'la': 'es', 'los': 'es', 'las': 'es', 'y': 'es', 'pero': 'es',
            'una': 'es', 'del': 'es', 'con': 'es', 'por': 'es', 'para': 'es',
            'yo': 'es', 'tú': 'es', 'él': 'es', 'ella': 'es', 'nosotros': 'es',
            
            # French
            'le': 'fr', 'les': 'fr', 'et': 'fr', 'ou': 'fr', 'mais': 'fr', 'est': 'fr',
            'un': 'fr', 'une': 'fr', 'du': 'fr', 'des': 'fr', 'dans': 'fr',
            'je': 'fr', 'tu': 'fr', 'il': 'fr', 'elle': 'fr', 'nous': 'fr',
            
            # Hindi (romanized)
            'mai': 'hi', 'mujhe': 'hi', 'tumhe': 'hi', 'usse': 'hi', 'humein': 'hi',
            'kya': 'hi', 'kaise': 'hi', 'kab': 'hi', 'kahaan': 'hi', 'kyun': 'hi',
            'bhi': 'hi', 'sirf': 'hi', 'bas': 'hi', 'abhi': 'hi', 'phir': 'hi',
            
            # Urdu (romanized)
            'main': 'ur', 'mein': 'ur', 'aap': 'ur', 'tum': 'ur', 'woh': 'ur',
            'ka': 'ur', 'ki': 'ur', 'ke': 'ur', 'ko': 'ur', 'se': 'ur',
            'aur': 'ur', 'ya': 'ur', 'lekin': 'ur', 'agar': 'ur', 'hai': 'ur',
            'nahi': 'ur', 'nahin': 'ur', 'haan': 'ur', 'theek': 'ur', 'accha': 'ur',
            
            # Arabic (romanized)
            'ana': 'ar', 'anta': 'ar', 'huwa': 'ar', 'hiya': 'ar', 'nahnu': 'ar',
            'fi': 'ar', 'min': 'ar', 'ila': 'ar', 'wa': 'ar', 'la': 'ar'
        }
        
        # Romanization patterns
        self.romanization_patterns = {
            'ur': [
                r'\b(main|mein|aap|tum|woh|yeh|hai|hain|ka|ki|ke|ko|se|aur|lekin)\b',
                r'\b(allah|inshallah|mashallah|bismillah|salam|khuda|hafiz)\b',
                r'\b(theek|accha|nahi|nahin|haan|ghar|dost|paani)\b'
            ],
            'hi': [
                r'\b(mai|mujhe|tumhe|usse|bhi|sirf|bas|abhi|phir|tab|jab)\b',
                r'\b(namaste|dhanyawad|kripaya|samay|ghar|paani|khana)\b',
                r'\b(raj|singh|kumar|sharma|gupta|verma|agarwal)\b'
            ],
            'ar': [
                r'\b(ana|anta|huwa|hiya|nahnu|fi|min|ila|wa|la)\b',
                r'\b(allah|bismillah|inshallah|mashallah|salam|habibi)\b',
                r'\b(ahlan|marhaba|shukran|yalla|akhi|ukhti)\b'
            ]
        }
        
        # Script confidence multipliers
        self.script_multipliers = {
            'ur': 1.2, 'hi': 1.1, 'ar': 1.1, 'fa': 1.1,
            'en': 1.0, 'es': 1.0, 'fr': 1.0, 'de': 1.0
        }
    
    def _normalize_language_code(self, language: str) -> str:
        """Normalize language name to ISO code."""
        language_map = {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'hindi': 'hi', 'urdu': 'ur', 'arabic': 'ar', 'persian': 'fa',
            'italian': 'it', 'portuguese': 'pt', 'turkish': 'tr'
        }
        normalized = language.lower().strip()
        return language_map.get(normalized, normalized[:2])
    
    def _detect_romanized_language(self, text: str) -> Optional[Tuple[str, float]]:
        """Detect romanized language patterns."""
        words = text.lower().split()
        if not words:
            return None
        
        for lang_code, patterns in self.romanization_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, text, re.IGNORECASE))
            
            if matches > 0:
                confidence = min(matches / len(words), 1.0) * 0.8
                if confidence >= 0.2:
                    return (lang_code, confidence)
        
        return None
    
    def _detect_with_fallback(self, text: str, user_languages: List[str] = None) -> Tuple[str, float]:
        """Enhanced detection with multiple fallback strategies."""
        if user_languages is None:
            user_languages = []
        
        # Normalize user languages
        user_langs_normalized = [self._normalize_language_code(lang) for lang in user_languages]
        
        # Check function words first
        words = text.lower().split()
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.function_words:
                func_lang = self.function_words[clean_word]
                is_user_lang = func_lang in user_langs_normalized
                confidence = 0.9 if is_user_lang else 0.8
                confidence *= self.script_multipliers.get(func_lang, 1.0)
                return (func_lang, min(confidence, 1.0))
        
        # Check romanization patterns
        romanized_result = self._detect_romanized_language(text)
        if romanized_result:
            lang, confidence = romanized_result
            is_user_lang = lang in user_langs_normalized
            if is_user_lang:
                confidence = max(confidence, self.user_language_confidence_threshold)
            if confidence >= self.romanized_confidence_threshold:
                confidence *= self.script_multipliers.get(lang, 1.0)
                return (lang, min(confidence, 1.0))
        
        # Use base detector
        base_lang = self.base_detector.detect_primary_language(text)
        if base_lang:
            base_confidence = 0.6  # Default confidence for base detector
            is_user_lang = base_lang in user_langs_normalized
            if is_user_lang:
                base_confidence = max(base_confidence, self.user_language_confidence_threshold)
            base_confidence *= self.script_multipliers.get(base_lang, 1.0)
            return (base_lang, min(base_confidence, 1.0))
        
        return ('unknown', 0.0)
    
    def _get_context_window(self, total_words: int) -> Dict[str, int]:
        """Get adaptive context window based on text length."""
        for window_name, settings in self.context_windows.items():
            if total_words <= settings['text_threshold']:
                return settings
        return self.context_windows['long']
    
    def _create_phrase_clusters(self, words: List[str], user_languages: List[str] = None) -> List[PhraseCluster]:
        """Create phrase clusters using adaptive sliding window."""
        if not words:
            return []
        
        if user_languages is None:
            user_languages = []
        
        user_langs_normalized = [self._normalize_language_code(lang) for lang in user_languages]
        clusters = []
        current_cluster = []
        current_language = 'unknown'
        current_confidence = 0.0
        start_index = 0
        
        # Get adaptive context window
        context_window = self._get_context_window(len(words))
        max_cluster_size = context_window['max_length']
        min_window_size = context_window['min_length']
        max_window_size = min(context_window['max_length'], 3)
        
        for i, word in enumerate(words):
            # Try different context windows
            best_detection = ('unknown', 0.0)
            
            for window_size in range(min_window_size, min(max_window_size + 1, len(words) - i + 1)):
                window_text = ' '.join(words[i:i + window_size])
                lang, confidence = self._detect_with_fallback(window_text, user_languages)
                
                if confidence > best_detection[1]:
                    best_detection = (lang, confidence)
            
            detected_lang, detected_confidence = best_detection
            
            # If language changes or cluster is full, finalize current cluster
            if (detected_lang != current_language or 
                len(current_cluster) >= max_cluster_size):
                
                if current_cluster:
                    is_user_lang = current_language in user_langs_normalized
                    clusters.append(PhraseCluster(
                        words=current_cluster.copy(),
                        text=' '.join(current_cluster),
                        language=current_language,
                        confidence=current_confidence,
                        start_index=start_index,
                        end_index=start_index + len(current_cluster) - 1,
                        is_user_language=is_user_lang
                    ))
                
                # Start new cluster
                current_cluster = [word]
                current_language = detected_lang
                current_confidence = detected_confidence
                start_index = i
            else:
                # Add to current cluster
                current_cluster.append(word)
                # Update confidence (weighted average)
                current_confidence = (current_confidence * 0.7) + (detected_confidence * 0.3)
        
        # Finalize last cluster
        if current_cluster:
            is_user_lang = current_language in user_langs_normalized
            clusters.append(PhraseCluster(
                words=current_cluster.copy(),
                text=' '.join(current_cluster),
                language=current_language,
                confidence=current_confidence,
                start_index=start_index,
                end_index=start_index + len(current_cluster) - 1,
                is_user_language=is_user_lang
            ))
        
        return clusters
    
    def _detect_switch_points(self, clusters: List[PhraseCluster]) -> List[int]:
        """Detect code-switching points between phrase clusters."""
        switch_points = []
        
        for i in range(1, len(clusters)):
            prev_cluster = clusters[i - 1]
            curr_cluster = clusters[i]
            
            # Switch detected if languages differ and both have sufficient confidence
            if (prev_cluster.language != curr_cluster.language and
                prev_cluster.language != 'unknown' and
                curr_cluster.language != 'unknown' and
                (prev_cluster.confidence >= self.user_language_confidence_threshold or
                 curr_cluster.confidence >= self.user_language_confidence_threshold)):
                
                switch_points.append(curr_cluster.start_index)
        
        return switch_points
    
    def _generate_cache_key(self, text: str, user_languages: List[str] = None) -> str:
        """Generate cache key for text and user languages."""
        if user_languages is None:
            user_languages = []
        
        normalized_text = text.lower().strip()
        sorted_languages = ','.join(sorted(user_languages))
        combined = f"{normalized_text}|{sorted_languages}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def analyze_with_user_guidance(self, text: str, user_languages: List[str] = None) -> EnhancedDetectionResult:
        """Enhanced analysis with user language guidance.
        
        Args:
            text: Input text to analyze.
            user_languages: List of languages the user typically uses.
            
        Returns:
            EnhancedDetectionResult with detailed analysis.
        """
        if not text or not text.strip():
            return EnhancedDetectionResult(
                tokens=[], phrases=[], switch_points=[], confidence=0.0,
                user_language_match=False, detected_languages=[],
                romanization_detected=False
            )
        
        if user_languages is None:
            user_languages = []
        
        # Check cache first
        cache_key = self._generate_cache_key(text, user_languages)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Segment text into words
        words = text.split()
        if not words:
            return EnhancedDetectionResult(
                tokens=[], phrases=[], switch_points=[], confidence=0.0,
                user_language_match=False, detected_languages=[],
                romanization_detected=False
            )
        
        # Create phrase clusters
        clusters = self._create_phrase_clusters(words, user_languages)
        
        # Detect switch points
        switch_points = self._detect_switch_points(clusters)
        
        # Convert to tokens for compatibility
        tokens = []
        for cluster in clusters:
            for word in cluster.words:
                tokens.append({
                    'word': word,
                    'lang': cluster.language,
                    'language': cluster.language,
                    'confidence': cluster.confidence
                })
        
        # Calculate overall confidence
        total_confidence = sum(cluster.confidence for cluster in clusters)
        overall_confidence = total_confidence / len(clusters) if clusters else 0.0
        
        # Get detected languages
        detected_languages = list(set(
            cluster.language for cluster in clusters 
            if cluster.language != 'unknown'
        ))
        
        # Check for romanization
        romanization_detected = any(
            self._detect_romanized_language(cluster.text) 
            for cluster in clusters
        )
        
        # Check user language match
        user_langs_normalized = [self._normalize_language_code(lang) for lang in user_languages]
        user_language_match = (
            len(user_langs_normalized) > 0 and
            all(lang in detected_languages for lang in user_langs_normalized)
        )
        
        result = EnhancedDetectionResult(
            tokens=tokens,
            phrases=clusters,
            switch_points=switch_points,
            confidence=overall_confidence,
            user_language_match=user_language_match,
            detected_languages=detected_languages,
            romanization_detected=romanization_detected
        )
        
        # Cache the result
        self.cache.set(cache_key, result)
        
        return result
    
    def detect_code_switching(self, text: str, user_languages: List[str] = None) -> EnhancedDetectionResult:
        """Detect code-switching in text (alias for analyze_with_user_guidance).
        
        Args:
            text: Input text to analyze.
            user_languages: List of languages the user typically uses.
            
        Returns:
            EnhancedDetectionResult with detailed analysis.
        """
        return self.analyze_with_user_guidance(text, user_languages)
    
    def get_detection_statistics(self, result: EnhancedDetectionResult) -> Dict[str, any]:
        """Get detailed statistics about the detection result."""
        language_counts = {}
        confidence_sums = {}
        phrase_counts = {}
        
        # Token-level statistics
        for token in result.tokens:
            lang = token['lang']
            language_counts[lang] = language_counts.get(lang, 0) + 1
            confidence_sums[lang] = confidence_sums.get(lang, 0) + token['confidence']
        
        # Phrase-level statistics
        for phrase in result.phrases:
            lang = phrase.language
            phrase_counts[lang] = phrase_counts.get(lang, 0) + 1
        
        token_stats = []
        for lang in language_counts:
            token_stats.append({
                'language': lang,
                'token_count': language_counts[lang],
                'phrase_count': phrase_counts.get(lang, 0),
                'average_confidence': confidence_sums[lang] / language_counts[lang],
                'percentage': (language_counts[lang] / len(result.tokens)) * 100
            })
        
        return {
            'total_tokens': len(result.tokens),
            'total_phrases': len(result.phrases),
            'total_switch_points': len(result.switch_points),
            'overall_confidence': result.confidence,
            'user_language_match': result.user_language_match,
            'detected_languages': result.detected_languages,
            'romanization_detected': result.romanization_detected,
            'language_breakdown': sorted(token_stats, key=lambda x: x['token_count'], reverse=True),
            'average_words_per_phrase': len(result.tokens) / max(len(result.phrases), 1),
            'switch_density': len(result.switch_points) / len(result.tokens) if result.tokens else 0
        }