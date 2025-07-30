"""Code-switch point detection for multilingual text."""

import re
from typing import List, Dict, Tuple, Optional
from .language_detector import LanguageDetector


class SwitchPoint:
    """Represents a code-switching point in text."""
    
    def __init__(self, position: int, from_lang: str, to_lang: str, 
                 confidence: float = 1.0, context: str = ""):
        self.position = position
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.confidence = confidence
        self.context = context
    
    def __repr__(self):
        return f"SwitchPoint(pos={self.position}, {self.from_lang}->{self.to_lang})"


class SwitchPointDetector:
    """Detects code-switching points in multilingual text."""
    
    def __init__(self, language_detector: Optional[LanguageDetector] = None):
        """Initialize the switch point detector.
        
        Args:
            language_detector: Language detector instance. Creates new one if None.
        """
        self.language_detector = language_detector or LanguageDetector()
        self.min_segment_length = 3
        self.context_window = 10
        
    def detect_sentence_level_switches(self, text: str) -> List[SwitchPoint]:
        """Detect code-switches between sentences.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            List of SwitchPoint objects.
        """
        sentence_data = self.language_detector.detect_sentence_languages(text)
        if len(sentence_data) < 2:
            return []
        
        switches = []
        current_pos = 0
        
        for i in range(1, len(sentence_data)):
            prev_lang = sentence_data[i-1]["language"]
            curr_lang = sentence_data[i]["language"]
            
            if prev_lang != curr_lang and prev_lang != "unknown" and curr_lang != "unknown":
                prev_sentence = sentence_data[i-1]["sentence"]
                current_pos += len(prev_sentence) + 1  # +1 for space/punctuation
                
                context_start = max(0, current_pos - self.context_window)
                context_end = min(len(text), current_pos + self.context_window)
                context = text[context_start:context_end]
                
                switches.append(SwitchPoint(
                    position=current_pos,
                    from_lang=prev_lang,
                    to_lang=curr_lang,
                    confidence=0.8,  # Medium confidence for sentence-level
                    context=context
                ))
            else:
                current_pos += len(sentence_data[i-1]["sentence"]) + 1
        
        return switches
    
    def detect_word_level_switches(self, text: str) -> List[SwitchPoint]:
        """Detect code-switches at word boundaries.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            List of SwitchPoint objects.
        """
        words = self._tokenize_words(text)
        if len(words) < 2:
            return []
        
        switches = []
        current_pos = 0
        
        for i in range(len(words) - 1):
            word1 = words[i]
            word2 = words[i + 1]
            
            lang1 = self.language_detector.detect_primary_language(word1)
            lang2 = self.language_detector.detect_primary_language(word2)
            
            if (lang1 and lang2 and lang1 != lang2 and 
                len(word1) >= self.min_segment_length and 
                len(word2) >= self.min_segment_length):
                
                word_end_pos = current_pos + len(word1)
                context_start = max(0, word_end_pos - self.context_window)
                context_end = min(len(text), word_end_pos + self.context_window)
                context = text[context_start:context_end]
                
                switches.append(SwitchPoint(
                    position=word_end_pos,
                    from_lang=lang1,
                    to_lang=lang2,
                    confidence=0.6,  # Lower confidence for word-level
                    context=context
                ))
            
            current_pos += len(word1) + 1  # +1 for space
        
        return switches
    
    def detect_all_switches(self, text: str) -> List[SwitchPoint]:
        """Detect all code-switching points in text.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Sorted list of all SwitchPoint objects.
        """
        sentence_switches = self.detect_sentence_level_switches(text)
        word_switches = self.detect_word_level_switches(text)
        
        all_switches = sentence_switches + word_switches
        all_switches.sort(key=lambda x: x.position)
        
        return self._deduplicate_switches(all_switches)
    
    def get_switch_statistics(self, text: str) -> Dict[str, any]:
        """Get statistics about code-switching in the text.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Dict with switching statistics.
        """
        switches = self.detect_all_switches(text)
        languages = set()
        
        for switch in switches:
            languages.add(switch.from_lang)
            languages.add(switch.to_lang)
        
        return {
            "total_switches": len(switches),
            "unique_languages": len(languages),
            "languages": list(languages),
            "switch_density": len(switches) / len(text.split()) if text.split() else 0,
            "avg_confidence": sum(s.confidence for s in switches) / len(switches) if switches else 0
        }
    
    def visualize_switches(self, text: str) -> str:
        """Create a visual representation of code-switches.
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Text with switch points marked.
        """
        switches = self.detect_all_switches(text)
        if not switches:
            return text
        
        result = ""
        last_pos = 0
        
        for switch in switches:
            result += text[last_pos:switch.position]
            result += f" [{switch.from_lang}->{switch.to_lang}] "
            last_pos = switch.position
        
        result += text[last_pos:]
        return result
    
    def _tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words.
        
        Args:
            text: Text to tokenize.
            
        Returns:
            List of words.
        """
        words = re.findall(r'\b\w+\b', text)
        return [word for word in words if len(word) >= self.min_segment_length]
    
    def _deduplicate_switches(self, switches: List[SwitchPoint]) -> List[SwitchPoint]:
        """Remove duplicate switch points that are very close to each other.
        
        Args:
            switches: List of switch points.
            
        Returns:
            Deduplicated list of switch points.
        """
        if not switches:
            return []
        
        deduplicated = [switches[0]]
        min_distance = 5  # Minimum distance between switches
        
        for switch in switches[1:]:
            last_switch = deduplicated[-1]
            if (abs(switch.position - last_switch.position) > min_distance or
                switch.from_lang != last_switch.from_lang or
                switch.to_lang != last_switch.to_lang):
                deduplicated.append(switch)
        
        return deduplicated