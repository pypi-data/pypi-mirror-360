"""Optimized code-switch detection with improved accuracy for underserved languages."""

import re
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import functools
import hashlib
import unicodedata
from .language_detector import LanguageDetector


@dataclass
class OptimizedResult:
    """Optimized detection result with improved accuracy."""
    tokens: List[Dict[str, any]]
    phrases: List[Dict[str, any]]
    switch_points: List[int]
    confidence: float
    user_language_match: bool
    detected_languages: List[str]
    romanization_detected: bool
    native_script_detected: bool


class OptimizedCodeSwitchDetector:
    """Optimized detector with comprehensive language support and improved accuracy."""
    
    def __init__(self, base_detector: Optional[LanguageDetector] = None):
        """Initialize optimized detector."""
        self.base_detector = base_detector or LanguageDetector()
        self.cache = {}
        
        # Improved confidence thresholds
        self.high_confidence_threshold = 0.85
        self.medium_confidence_threshold = 0.6
        self.low_confidence_threshold = 0.4
        
        # Comprehensive function words with high-frequency terms
        self.function_words = self._build_comprehensive_function_words()
        
        # Language-specific patterns for underserved languages
        self.language_patterns = self._build_language_patterns()
        
        # Native script detection patterns
        self.script_patterns = self._build_script_patterns()
        
        # Improved romanization patterns
        self.romanization_patterns = self._build_romanization_patterns()
        
        # Language code normalization
        self.language_codes = self._build_language_codes()
    
    def _build_comprehensive_function_words(self) -> Dict[str, str]:
        """Build comprehensive function word mapping."""
        return {
            # English (expanded)
            'the': 'en', 'and': 'en', 'or': 'en', 'but': 'en', 'is': 'en', 'are': 'en', 'was': 'en', 'were': 'en',
            'a': 'en', 'an': 'en', 'to': 'en', 'for': 'en', 'of': 'en', 'in': 'en', 'on': 'en', 'at': 'en',
            'i': 'en', 'you': 'en', 'he': 'en', 'she': 'en', 'it': 'en', 'we': 'en', 'they': 'en', 'them': 'en',
            'this': 'en', 'that': 'en', 'these': 'en', 'those': 'en', 'my': 'en', 'your': 'en', 'his': 'en', 'her': 'en',
            'have': 'en', 'has': 'en', 'had': 'en', 'will': 'en', 'would': 'en', 'can': 'en', 'could': 'en',
            'hello': 'en', 'world': 'en', 'today': 'en', 'very': 'en', 'good': 'en', 'bad': 'en', 'yes': 'en', 'no': 'en',
            
            # Spanish (expanded)
            'el': 'es', 'la': 'es', 'los': 'es', 'las': 'es', 'y': 'es', 'pero': 'es', 'es': 'es', 'está': 'es',
            'una': 'es', 'del': 'es', 'con': 'es', 'por': 'es', 'para': 'es', 'en': 'es', 'de': 'es',
            'yo': 'es', 'tú': 'es', 'él': 'es', 'ella': 'es', 'nosotros': 'es', 'ellos': 'es', 'ellas': 'es',
            'hola': 'es', 'mundo': 'es', 'hoy': 'es', 'muy': 'es', 'bueno': 'es', 'malo': 'es', 'sí': 'es', 'cómo': 'es',
            'gato': 'es', 'gatos': 'es', 'casa': 'es', 'bien': 'es', 'gracias': 'es',
            
            # French (expanded)
            'le': 'fr', 'les': 'fr', 'et': 'fr', 'ou': 'fr', 'mais': 'fr', 'est': 'fr', 'sont': 'fr',
            'un': 'fr', 'une': 'fr', 'du': 'fr', 'des': 'fr', 'dans': 'fr', 'avec': 'fr', 'sur': 'fr',
            'je': 'fr', 'tu': 'fr', 'il': 'fr', 'elle': 'fr', 'nous': 'fr', 'vous': 'fr', 'ils': 'fr', 'elles': 'fr',
            'bonjour': 'fr', 'monde': 'fr', 'aujourd': 'fr', 'hui': 'fr', 'très': 'fr', 'suis': 'fr', 'chat': 'fr',
            
            # German (expanded)
            'der': 'de', 'die': 'de', 'das': 'de', 'und': 'de', 'oder': 'de', 'aber': 'de', 'ist': 'de', 'sind': 'de',
            'ein': 'de', 'eine': 'de', 'dem': 'de', 'den': 'de', 'mit': 'de', 'für': 'de', 'von': 'de', 'zu': 'de',
            'ich': 'de', 'du': 'de', 'er': 'de', 'sie': 'de', 'wir': 'de', 'ihr': 'de',
            'hallo': 'de', 'welt': 'de', 'heute': 'de', 'sehr': 'de', 'gut': 'de', 'bin': 'de', 'müde': 'de',
            
            # Hindi (romanized - expanded)
            'mai': 'hi', 'main': 'hi', 'mujhe': 'hi', 'tumhe': 'hi', 'usse': 'hi', 'humein': 'hi', 'unhe': 'hi',
            'kya': 'hi', 'kaise': 'hi', 'kab': 'hi', 'kahaan': 'hi', 'kyun': 'hi', 'kaun': 'hi',
            'bhi': 'hi', 'sirf': 'hi', 'bas': 'hi', 'abhi': 'hi', 'phir': 'hi', 'tab': 'hi', 'jab': 'hi',
            'namaste': 'hi', 'ghar': 'hi', 'paani': 'hi', 'khana': 'hi', 'accha': 'hi', 'bura': 'hi',
            'raha': 'hi', 'rahe': 'hi', 'rahi': 'hi', 'hoon': 'hi', 'hain': 'hi', 'hai': 'hi',
            
            # Urdu (romanized - expanded)
            'main': 'ur', 'mein': 'ur', 'aap': 'ur', 'tum': 'ur', 'woh': 'ur', 'yeh': 'ur',
            'ka': 'ur', 'ki': 'ur', 'ke': 'ur', 'ko': 'ur', 'se': 'ur', 'par': 'ur',
            'aur': 'ur', 'ya': 'ur', 'lekin': 'ur', 'agar': 'ur', 'hai': 'ur', 'hain': 'ur',
            'nahi': 'ur', 'nahin': 'ur', 'haan': 'ur', 'ji': 'ur', 'theek': 'ur', 'accha': 'ur',
            'salam': 'ur', 'kaise': 'ur', 'kya': 'ur', 'kahan': 'ur',
            
            # Arabic (romanized - expanded)
            'ana': 'ar', 'anta': 'ar', 'anti': 'ar', 'huwa': 'ar', 'hiya': 'ar', 'nahnu': 'ar',
            'fi': 'ar', 'min': 'ar', 'ila': 'ar', 'ala': 'ar', 'wa': 'ar', 'la': 'ar', 'ma': 'ar',
            'salam': 'ar', 'alaikum': 'ar', 'marhaba': 'ar', 'ahlan': 'ar', 'habibi': 'ar',
            'allah': 'ar', 'inshallah': 'ar', 'mashallah': 'ar', 'alhamdulillah': 'ar',
            
            # Portuguese (expanded)
            'os': 'pt', 'as': 'pt', 'um': 'pt', 'uma': 'pt', 'do': 'pt', 'da': 'pt', 'no': 'pt', 'na': 'pt',
            'em': 'pt', 'com': 'pt', 'por': 'pt', 'para': 'pt', 'de': 'pt', 'que': 'pt',
            'eu': 'pt', 'você': 'pt', 'ele': 'pt', 'ela': 'pt', 'nós': 'pt', 'eles': 'pt', 'elas': 'pt',
            'olá': 'pt', 'mundo': 'pt', 'hoje': 'pt', 'muito': 'pt', 'bom': 'pt', 'estou': 'pt', 'cansado': 'pt',
            
            # Italian (expanded)
            'il': 'it', 'lo': 'it', 'la': 'it', 'gli': 'it', 'le': 'it', 'un': 'it', 'una': 'it',
            'di': 'it', 'del': 'it', 'della': 'it', 'nel': 'it', 'nella': 'it', 'con': 'it', 'per': 'it',
            'io': 'it', 'tu': 'it', 'lui': 'it', 'lei': 'it', 'noi': 'it', 'voi': 'it', 'loro': 'it',
            'ciao': 'it', 'mondo': 'it', 'oggi': 'it', 'molto': 'it', 'bene': 'it', 'sono': 'it', 'stanco': 'it',
        }
    
    def _build_language_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for underserved languages."""
        return {
            # African languages
            'sw': ['habari', 'jambo', 'asante', 'karibu', 'ndio', 'hapana', 'mzuri', 'nzuri', 'nina', 'una'],
            'xh': ['sawubona', 'unjani', 'enkosi', 'ndiyakuthanda', 'ubuntu', 'molo', 'nkosi'],
            'zu': ['sawubona', 'unjani', 'ngiyabonga', 'ngiyakuthanda', 'yebo', 'cha', 'ngikhuluma'],
            'yo': ['bawo', 'pele', 'ese', 'mo', 'wa', 'ti', 'ni', 'se', 'ki', 'bi'],
            'ig': ['ndewo', 'kedu', 'dalu', 'mba', 'na', 'ya', 'ka', 'nke', 'ahu', 'ihe'],
            'ha': ['sannu', 'yaya', 'na', 'gode', 'ina', 'ka', 'da', 'ba', 'ko', 'mai'],
            
            # South Asian languages
            'bn': ['ami', 'apni', 'tumi', 'se', 'amra', 'tara', 'kemon', 'bhalo', 'kharap', 'bangla'],
            'ta': ['naan', 'neenga', 'avan', 'aval', 'naanga', 'avanga', 'eppadi', 'nalla', 'tamil', 'pesuren'],
            'te': ['nenu', 'meeru', 'atanu', 'aame', 'manam', 'vallaru', 'ela', 'bagundi', 'telugu', 'matladutunnanu'],
            'gu': ['hun', 'tame', 'te', 'tenu', 'ame', 'te', 'kevi', 'rite', 'saras', 'gujarati'],
            'mr': ['mi', 'tu', 'to', 'ti', 'aamhi', 'te', 'kase', 'chan', 'marathi', 'bolto'],
            'pa': ['main', 'tussi', 'oh', 'onu', 'assi', 'ohna', 'kive', 'changa', 'punjabi', 'bolda'],
            
            # Southeast Asian languages
            'id': ['saya', 'anda', 'dia', 'kami', 'mereka', 'bagaimana', 'baik', 'indonesia', 'berbahasa'],
            'ms': ['saya', 'awak', 'dia', 'kami', 'mereka', 'bagaimana', 'baik', 'melayu', 'cakap'],
            'tl': ['ako', 'ikaw', 'siya', 'kami', 'sila', 'paano', 'mabuti', 'pilipino', 'tagalog'],
            'th': ['chan', 'khun', 'kao', 'rao', 'khao', 'yang', 'rai', 'dee', 'thai', 'phasa'],
            'vi': ['toi', 'ban', 'ho', 'chung', 'ta', 'nhu', 'the', 'nao', 'tot', 'viet', 'tieng'],
            
            # East Asian romanized
            'ja': ['watashi', 'anata', 'kare', 'kanojo', 'watashitachi', 'karera', 'dou', 'ii', 'nihongo'],
            'ko': ['na', 'neol', 'geu', 'geunyeo', 'uri', 'geudeul', 'eotteoke', 'joeun', 'hanguk'],
            'zh': ['wo', 'ni', 'ta', 'women', 'tamen', 'zenme', 'hao', 'zhongwen', 'hanyu'],
            
            # European minority languages
            'eu': ['ni', 'zu', 'hura', 'gu', 'zuek', 'haiek', 'nola', 'ona', 'euskera', 'euskera'],
            'ca': ['jo', 'tu', 'ell', 'ella', 'nosaltres', 'ells', 'com', 'bo', 'català', 'parla'],
            'cy': ['fi', 'ti', 'ef', 'hi', 'ni', 'nhw', 'sut', 'da', 'cymraeg', 'siarad'],
            
            # Slavic languages
            'ru': ['ya', 'ty', 'on', 'ona', 'my', 'oni', 'kak', 'khorosho', 'russki', 'govoryu'],
            'pl': ['ja', 'ty', 'on', 'ona', 'my', 'oni', 'jak', 'dobrze', 'polski', 'mowie'],
            'cs': ['ja', 'ty', 'on', 'ona', 'my', 'oni', 'jak', 'dobre', 'cesky', 'mluvim'],
            
            # Indigenous languages (basic patterns)
            'mi': ['kia', 'ora', 'ahau', 'koe', 'ia', 'tatou', 'ratou', 'pehea', 'pai', 'maori'],
            'haw': ['aloha', 'au', 'oe', 'ia', 'kakou', 'lakou', 'pehea', 'maikai', 'hawaii'],
            
            # Hebrew
            'he': ['ani', 'ata', 'at', 'hu', 'hi', 'anachnu', 'atem', 'hen', 'eich', 'tov', 'shalom'],
        }
    
    def _build_script_patterns(self) -> Dict[str, str]:
        """Build native script detection patterns."""
        return {
            # Fixed Unicode script ranges - using proper hex notation
            'arabic': r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+',
            'chinese': r'[\u4E00-\u9FFF\u3400-\u4DBF]+',  # Fixed: removed invalid ranges
            'japanese': r'[\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF]+',
            'korean': r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]+',
            'devanagari': r'[\u0900-\u097F]+',  # Hindi, Sanskrit, Marathi
            'bengali': r'[\u0980-\u09FF]+',
            'gujarati': r'[\u0A80-\u0AFF]+',
            'tamil': r'[\u0B80-\u0BFF]+',
            'telugu': r'[\u0C00-\u0C7F]+',
            'hebrew': r'[\u0590-\u05FF\uFB1D-\uFB4F]+',
            'cyrillic': r'[\u0400-\u04FF\u0500-\u052F]+',
            'thai': r'[\u0E00-\u0E7F]+',
            'georgian': r'[\u10A0-\u10FF\u2D00-\u2D2F]+',
            'armenian': r'[\u0530-\u058F\uFB13-\uFB17]+',
        }
    
    def _build_romanization_patterns(self) -> Dict[str, List[str]]:
        """Build improved romanization patterns."""
        return {
            'ur': [
                r'\b(main|mein|aap|tum|woh|yeh|hai|hain|ka|ki|ke|ko|se|par|tak)\b',
                r'\b(aur|ya|lekin|agar|kyun|kya|kaise|kahan|kab|kaun)\b',
                r'\b(nahi|nahin|haan|ji|theek|accha|burra|bara|chota)\b',
                r'\b(salam|alaikum|allah|inshallah|mashallah|bismillah)\b',
                r'\b(ghar|shaher|dost|paani|khana|kitab|kaam|waqt)\b',
            ],
            'hi': [
                r'\b(mai|mujhe|tumhe|usse|isse|humein|unhe|inhe)\b',
                r'\b(kya|kaise|kab|kahaan|kyun|kaun|kitna|kitni)\b',
                r'\b(bhi|sirf|bas|abhi|phir|tab|jab|kal|parso)\b',
                r'\b(namaste|dhanyawad|kripaya|samay|desh|ghar)\b',
                r'\b(raha|rahe|rahi|hoon|hain|hai|tha|the|thi)\b',
            ],
            'ar': [
                r'\b(ana|anta|anti|huwa|hiya|nahnu|antum|hum)\b',
                r'\b(fi|min|ila|ala|an|ma|la|wa|lam|lan)\b',
                r'\b(hatha|hadhihi|tilka|dhalika|kayf|mata|ayna)\b',
                r'\b(salam|alaikum|marhaba|ahlan|habibi|akhi|ukhti)\b',
                r'\b(allah|bismillah|inshallah|mashallah|alhamdulillah)\b',
            ],
            'bn': [
                r'\b(ami|apni|tumi|se|amra|tara|oder|tader)\b',
                r'\b(ki|kemon|kobe|kothay|keno|kar|koto)\b',
                r'\b(ache|chilo|hobe|korchi|jabo|asbo)\b',
                r'\b(bhalo|kharap|sundor|bangla|desh)\b',
            ],
            'ta': [
                r'\b(naan|neenga|avan|aval|naanga|avanga)\b',
                r'\b(enna|eppadi|eppo|enga|yen|yaar|evlo)\b',
                r'\b(irukku|irundhen|varum|poren|varen)\b',
                r'\b(nalla|ketta|azhaga|tamil|nadu)\b',
            ],
            'sw': [
                r'\b(mimi|wewe|yeye|sisi|ninyi|wao)\b',
                r'\b(nini|vipi|lini|wapi|kwa|nini|ngapi)\b',
                r'\b(nina|una|ana|tuna|mna|wana)\b',
                r'\b(habari|jambo|asante|karibu|ndio|hapana)\b',
            ],
        }
    
    def _build_language_codes(self) -> Dict[str, str]:
        """Build comprehensive language code mapping."""
        return {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'dutch': 'nl', 'swedish': 'sv',
            'norwegian': 'no', 'danish': 'da', 'finnish': 'fi', 'russian': 'ru',
            'polish': 'pl', 'czech': 'cs', 'slovak': 'sk', 'hungarian': 'hu',
            'hindi': 'hi', 'urdu': 'ur', 'arabic': 'ar', 'persian': 'fa',
            'bengali': 'bn', 'tamil': 'ta', 'telugu': 'te', 'gujarati': 'gu',
            'marathi': 'mr', 'punjabi': 'pa', 'chinese': 'zh', 'japanese': 'ja',
            'korean': 'ko', 'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id',
            'malay': 'ms', 'filipino': 'tl', 'tagalog': 'tl', 'swahili': 'sw',
            'yoruba': 'yo', 'igbo': 'ig', 'hausa': 'ha', 'xhosa': 'xh',
            'zulu': 'zu', 'hebrew': 'he', 'greek': 'el', 'turkish': 'tr',
            'basque': 'eu', 'catalan': 'ca', 'welsh': 'cy', 'irish': 'ga',
            'maori': 'mi', 'hawaiian': 'haw', 'esperanto': 'eo',
        }
    
    def _normalize_language_code(self, language: str) -> str:
        """Normalize language name to ISO code."""
        normalized = language.lower().strip()
        return self.language_codes.get(normalized, normalized[:2])
    
    def _detect_native_script(self, text: str) -> Optional[Tuple[str, float]]:
        """Detect native scripts in text."""
        # Count total non-space characters
        total_chars = len(re.sub(r'\s+', '', text))
        if total_chars == 0:
            return None
        
        best_match = None
        best_score = 0
        
        for script_name, pattern in self.script_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                # Calculate percentage of text that matches this script
                script_chars = sum(len(match) for match in matches)
                script_percentage = script_chars / total_chars
                
                # Only consider if significant portion is in this script (>20%)
                if script_percentage > 0.2:
                    confidence = min(script_percentage * 1.2, 1.0)
                    
                    if confidence > best_score:
                        # Map script to language
                        script_to_lang = {
                            'arabic': 'ar',
                            'chinese': 'zh', 
                            'japanese': 'ja',
                            'korean': 'ko',
                            'devanagari': 'hi',
                            'bengali': 'bn',
                            'gujarati': 'gu',
                            'tamil': 'ta',
                            'telugu': 'te',
                            'hebrew': 'he',
                            'cyrillic': 'ru',
                            'thai': 'th',
                        }
                        
                        lang = script_to_lang.get(script_name, script_name)
                        best_match = (lang, confidence)
                        best_score = confidence
        
        return best_match
    
    def _detect_by_patterns(self, text: str, user_languages: List[str] = None) -> Tuple[str, float]:
        """Enhanced pattern-based detection."""
        if user_languages is None:
            user_languages = []
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # 1. Check native scripts first (highest confidence)
        native_result = self._detect_native_script(text)
        if native_result:
            lang, confidence = native_result
            user_langs_normalized = [self._normalize_language_code(ul) for ul in user_languages]
            if lang in user_langs_normalized:
                confidence = min(confidence * 1.3, 1.0)  # Boost user languages
            return (lang, confidence)
        
        # 2. Check function words (high confidence)
        function_matches = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.function_words:
                func_lang = self.function_words[clean_word]
                function_matches[func_lang] = function_matches.get(func_lang, 0) + 1
        
        if function_matches:
            best_lang = max(function_matches.keys(), key=lambda x: function_matches[x])
            confidence = min(function_matches[best_lang] / len(words), 1.0) * 0.95  # High confidence for function words
            user_langs_normalized = [self._normalize_language_code(ul) for ul in user_languages]
            if best_lang in user_langs_normalized and best_lang != 'en':
                confidence = min(confidence * 1.2, 1.0)
            return (best_lang, confidence)
        
        # 3. Check language-specific patterns (medium confidence)
        pattern_scores = {}
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern_word in patterns:
                if pattern_word in text_lower:
                    score += 1
            if score > 0:
                pattern_scores[lang] = score / len(words)
        
        if pattern_scores:
            best_lang = max(pattern_scores.keys(), key=lambda x: pattern_scores[x])
            confidence = min(pattern_scores[best_lang] * 0.8, 1.0)
            return (best_lang, confidence)
        
        # 4. Check romanization patterns (medium confidence)
        for lang, patterns in self.romanization_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, text_lower, re.IGNORECASE))
            
            if matches > 0:
                confidence = min(matches / len(words) * 0.7, 1.0)
                return (lang, confidence)
        
        # 5. Fallback to base detector (low confidence)
        base_lang = self.base_detector.detect_primary_language(text)
        if base_lang and base_lang != 'unknown':
            return (base_lang, 0.5)  # Lower confidence for base detector
        
        return ('unknown', 0.0)
    
    def _create_optimized_phrases(self, words: List[str], user_languages: List[str] = None) -> List[Dict[str, any]]:
        """Create optimized phrase clusters with improved accuracy."""
        if not words:
            return []
        
        phrases = []
        current_phrase = []
        current_language = 'unknown'
        current_confidence = 0.0
        start_index = 0
        
        user_langs_normalized = [self._normalize_language_code(lang) for lang in user_languages or []]
        
        for i, word in enumerate(words):
            # Detect language for current word with context
            context_start = max(0, i - 1)
            context_end = min(len(words), i + 2)
            context_text = ' '.join(words[context_start:context_end])
            
            detected_lang, confidence = self._detect_by_patterns(context_text, user_languages)
            
            # Boost confidence for user languages, especially non-English
            if detected_lang in user_langs_normalized:
                if detected_lang != 'en':
                    confidence = min(confidence * 1.5, 1.0)
                else:
                    confidence = min(confidence * 1.1, 1.0)
            
            # Only create new phrase if language changes AND confidence is sufficient
            if (detected_lang != current_language and 
                confidence >= self.low_confidence_threshold and
                (current_confidence >= self.low_confidence_threshold or not current_phrase)):
                
                # Finalize current phrase
                if current_phrase:
                    phrases.append({
                        'words': current_phrase.copy(),
                        'text': ' '.join(current_phrase),
                        'language': current_language,
                        'confidence': current_confidence,
                        'start_index': start_index,
                        'end_index': start_index + len(current_phrase) - 1,
                        'is_user_language': current_language in user_langs_normalized
                    })
                
                # Start new phrase
                current_phrase = [word]
                current_language = detected_lang
                current_confidence = confidence
                start_index = i
            else:
                # Add to current phrase
                current_phrase.append(word)
                # Update confidence with weighted average
                if confidence > 0:
                    current_confidence = (current_confidence * 0.7) + (confidence * 0.3)
        
        # Finalize last phrase
        if current_phrase:
            phrases.append({
                'words': current_phrase.copy(),
                'text': ' '.join(current_phrase),
                'language': current_language,
                'confidence': current_confidence,
                'start_index': start_index,
                'end_index': start_index + len(current_phrase) - 1,
                'is_user_language': current_language in user_langs_normalized
            })
        
        return phrases
    
    def _detect_switch_points_optimized(self, phrases: List[Dict[str, any]]) -> List[int]:
        """Detect switch points with improved accuracy."""
        switch_points = []
        
        for i in range(1, len(phrases)):
            prev_phrase = phrases[i - 1]
            curr_phrase = phrases[i]
            
            # Only consider as switch if:
            # 1. Languages are different
            # 2. Both have sufficient confidence
            # 3. Neither is unknown
            if (prev_phrase['language'] != curr_phrase['language'] and
                prev_phrase['language'] != 'unknown' and
                curr_phrase['language'] != 'unknown' and
                prev_phrase['confidence'] >= self.medium_confidence_threshold and
                curr_phrase['confidence'] >= self.medium_confidence_threshold):
                
                switch_points.append(curr_phrase['start_index'])
        
        return switch_points
    
    def analyze_optimized(self, text: str, user_languages: List[str] = None) -> OptimizedResult:
        """Analyze text with optimized detection."""
        if not text or not text.strip():
            return OptimizedResult(
                tokens=[], phrases=[], switch_points=[], confidence=0.0,
                user_language_match=False, detected_languages=[],
                romanization_detected=False, native_script_detected=False
            )
        
        if user_languages is None:
            user_languages = []
        
        # Check cache
        cache_key = hashlib.md5(f"{text}|{','.join(user_languages)}".encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Segment into words
        words = text.split()
        if not words:
            return OptimizedResult(
                tokens=[], phrases=[], switch_points=[], confidence=0.0,
                user_language_match=False, detected_languages=[],
                romanization_detected=False, native_script_detected=False
            )
        
        # Create optimized phrases
        phrases = self._create_optimized_phrases(words, user_languages)
        
        # Detect switch points
        switch_points = self._detect_switch_points_optimized(phrases)
        
        # Convert to tokens
        tokens = []
        for phrase in phrases:
            for word in phrase['words']:
                tokens.append({
                    'word': word,
                    'lang': phrase['language'],
                    'language': phrase['language'],
                    'confidence': phrase['confidence']
                })
        
        # Calculate overall confidence
        total_confidence = sum(phrase['confidence'] for phrase in phrases)
        overall_confidence = total_confidence / len(phrases) if phrases else 0.0
        
        # Get detected languages
        # Get detected languages above confidence threshold
        detected_languages = [
            phrase['language'] for phrase in phrases
            if phrase['language'] != 'unknown' and phrase['confidence'] >= self.medium_confidence_threshold
        ]

        # Fallback: use highest-confidence language if none pass threshold
        if not detected_languages and phrases:
            top_phrase = max(phrases, key=lambda p: p['confidence'])
            if top_phrase['language'] != 'unknown':
                detected_languages = [top_phrase['language']]

        # Ensure uniqueness
        detected_languages = list(set(detected_languages))
        
        # Check for romanization and native scripts
        romanization_detected = any(
            any(re.search(pattern, text.lower()) for pattern in patterns)
            for patterns in self.romanization_patterns.values()
        )
        
        native_script_detected = self._detect_native_script(text) is not None
        
        # Check user language match
        user_langs_normalized = [self._normalize_language_code(lang) for lang in user_languages]
        user_language_match = (
            len(user_langs_normalized) > 0 and
            len(set(detected_languages) & set(user_langs_normalized)) > 0
        )
        
        result = OptimizedResult(
            tokens=tokens,
            phrases=phrases,
            switch_points=switch_points,
            confidence=overall_confidence,
            user_language_match=user_language_match,
            detected_languages=detected_languages,
            romanization_detected=romanization_detected,
            native_script_detected=native_script_detected
        )
        
        # Cache result
        self.cache[cache_key] = result
        
        return result