#!/usr/bin/env python3
"""Switch point refinement - more precise boundary detection using linguistic features."""

import numpy as np
import re
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict
import string

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from .ensemble_detector import EnsembleDetector
from .language_detector import DetectionResult


@dataclass
class SwitchPoint:
    """Represents a refined switch point."""
    position: int  # Character or token position
    confidence: float
    from_language: str
    to_language: str
    linguistic_features: Dict[str, Any]
    boundary_type: str  # 'word', 'phrase', 'sentence', 'punctuation'
    context_before: str
    context_after: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RefinementResult:
    """Result of switch point refinement."""
    original_switches: List[int]
    refined_switches: List[SwitchPoint]
    text: str
    tokens: List[str]
    token_languages: List[str]
    confidence_scores: List[float]
    linguistic_analysis: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['refined_switches'] = [s.to_dict() for s in self.refined_switches]
        return result
    
    def summary(self) -> str:
        """Generate summary of refinement."""
        return f"""
Switch Point Refinement Results:
===============================
Original switches: {len(self.original_switches)}
Refined switches: {len(self.refined_switches)}
Text length: {len(self.text)} characters
Tokens: {len(self.tokens)}

Refined Switch Points:
{self._format_switches()}
"""
    
    def _format_switches(self) -> str:
        """Format switch points for display."""
        lines = []
        for i, switch in enumerate(self.refined_switches):
            lines.append(
                f"  {i+1}. Pos {switch.position}: {switch.from_language} → {switch.to_language} "
                f"({switch.confidence:.3f}, {switch.boundary_type})"
            )
        return "\n".join(lines)


class LinguisticFeatureAnalyzer:
    """Analyze linguistic features for switch point refinement."""
    
    def __init__(self):
        """Initialize linguistic analyzer."""
        # Initialize spaCy if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                # Try to load multilingual model, fall back to English
                try:
                    self.nlp = spacy.load("xx_ent_wiki_sm")  # Multilingual
                except OSError:
                    try:
                        self.nlp = spacy.load("en_core_web_sm")  # English
                    except OSError:
                        print("⚠ No spaCy models available. Install with: python -m spacy download en_core_web_sm")
            except Exception as e:
                print(f"⚠ spaCy initialization failed: {e}")
        
        # Language-specific patterns
        self.language_patterns = {
            'english': {
                'function_words': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'},
                'common_endings': {'-ed', '-ing', '-ly', '-tion', '-ness', '-ment'},
                'articles': {'the', 'a', 'an'},
                'pronouns': {'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            },
            'spanish': {
                'function_words': {'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'pero', 'en', 'de', 'con', 'por', 'para'},
                'common_endings': {'-ar', '-er', '-ir', '-ado', '-ido', '-mente', '-ción', '-dad'},
                'articles': {'el', 'la', 'los', 'las', 'un', 'una'},
                'pronouns': {'yo', 'tú', 'él', 'ella', 'nosotros', 'vosotros', 'ellos', 'ellas', 'me', 'te', 'se', 'nos'}
            },
            'french': {
                'function_words': {'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'mais', 'dans', 'de', 'avec', 'par', 'pour'},
                'common_endings': {'-er', '-ir', '-re', '-é', '-ment', '-tion', '-té'},
                'articles': {'le', 'la', 'les', 'un', 'une'},
                'pronouns': {'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se'}
            }
        }
    
    def analyze_token_features(self, token: str, position: int, context: List[str]) -> Dict[str, Any]:
        """Analyze linguistic features of a token.
        
        Args:
            token: Token to analyze
            position: Position in sequence
            context: Surrounding tokens
            
        Returns:
            Dictionary of linguistic features
        """
        features = {
            'length': len(token),
            'is_punctuation': token in string.punctuation,
            'is_capitalized': token.istitle(),
            'is_all_caps': token.isupper(),
            'is_numeric': token.isdigit(),
            'has_digits': any(c.isdigit() for c in token),
            'is_alpha': token.isalpha(),
            'language_indicators': {}
        }
        
        # Language-specific features
        token_lower = token.lower()
        for lang, patterns in self.language_patterns.items():
            lang_score = 0
            
            # Check function words
            if token_lower in patterns['function_words']:
                lang_score += 3
            
            # Check articles
            if token_lower in patterns['articles']:
                lang_score += 2
            
            # Check pronouns
            if token_lower in patterns['pronouns']:
                lang_score += 2
            
            # Check endings
            for ending in patterns['common_endings']:
                if token_lower.endswith(ending):
                    lang_score += 1
                    break
            
            features['language_indicators'][lang] = lang_score
        
        # Positional features
        features['is_sentence_start'] = (
            position == 0 or 
            (position > 0 and context[position-1] in '.!?')
        )
        features['is_sentence_end'] = token.endswith('.') or token.endswith('!') or token.endswith('?')
        
        # Morphological features
        features['morphology'] = self._analyze_morphology(token)
        
        return features
    
    def _analyze_morphology(self, token: str) -> Dict[str, Any]:
        """Analyze morphological features of token."""
        morphology = {
            'prefix_count': 0,
            'suffix_count': 0,
            'compound_likely': False,
            'cognate_score': 0
        }
        
        # Simple prefix detection
        common_prefixes = ['un', 're', 'pre', 'dis', 'over', 'under', 'sub', 'super']
        for prefix in common_prefixes:
            if token.lower().startswith(prefix) and len(token) > len(prefix) + 2:
                morphology['prefix_count'] += 1
        
        # Simple suffix detection
        common_suffixes = ['ing', 'ed', 'er', 'est', 'ly', 'ness', 'ment', 'tion', 'able']
        for suffix in common_suffixes:
            if token.lower().endswith(suffix) and len(token) > len(suffix) + 2:
                morphology['suffix_count'] += 1
        
        # Compound word likelihood
        if len(token) > 8 and not any(c in token for c in string.punctuation):
            morphology['compound_likely'] = True
        
        return morphology
    
    def analyze_context_coherence(self, tokens: List[str], start_idx: int, end_idx: int) -> float:
        """Analyze coherence of a token sequence.
        
        Args:
            tokens: List of tokens
            start_idx: Start index of sequence
            end_idx: End index of sequence
            
        Returns:
            Coherence score (0-1)
        """
        if start_idx >= end_idx or start_idx < 0 or end_idx > len(tokens):
            return 0.0
        
        sequence = tokens[start_idx:end_idx]
        if not sequence:
            return 0.0
        
        coherence_score = 0.0
        total_factors = 0
        
        # Factor 1: Language consistency
        lang_scores = defaultdict(float)
        for token in sequence:
            features = self.analyze_token_features(token, 0, sequence)
            for lang, score in features['language_indicators'].items():
                lang_scores[lang] += score
        
        if lang_scores:
            max_lang_score = max(lang_scores.values())
            total_score = sum(lang_scores.values())
            if total_score > 0:
                coherence_score += max_lang_score / total_score
                total_factors += 1
        
        # Factor 2: Grammatical structure
        if self.nlp:
            try:
                text = ' '.join(sequence)
                doc = self.nlp(text)
                
                # Check for complete phrases/clauses
                has_subject = any(token.dep_ in ['nsubj', 'nsubjpass'] for token in doc)
                has_verb = any(token.pos_ == 'VERB' for token in doc)
                
                if has_subject and has_verb:
                    coherence_score += 0.5
                elif has_subject or has_verb:
                    coherence_score += 0.25
                
                total_factors += 1
                
            except Exception:
                # Fallback: simple heuristics
                pass
        
        # Factor 3: Punctuation boundaries
        starts_with_punct = sequence[0] in string.punctuation
        ends_with_punct = sequence[-1] in string.punctuation
        
        if starts_with_punct and ends_with_punct:
            coherence_score += 0.3
        elif starts_with_punct or ends_with_punct:
            coherence_score += 0.15
        
        total_factors += 1
        
        # Normalize score
        return coherence_score / max(total_factors, 1)


class SwitchPointRefiner:
    """Refines switch points using linguistic features and context analysis."""
    
    def __init__(self, detector: Optional[EnsembleDetector] = None):
        """Initialize switch point refiner.
        
        Args:
            detector: Language detector to use for analysis
        """
        self.detector = detector or EnsembleDetector()
        self.linguistic_analyzer = LinguisticFeatureAnalyzer()
        
        # Refinement parameters
        self.min_confidence_threshold = 0.5
        self.context_window = 3  # Tokens on each side for context
        self.boundary_preferences = {
            'sentence': 1.0,      # Prefer sentence boundaries
            'punctuation': 0.8,   # Punctuation marks
            'phrase': 0.6,        # Phrase boundaries
            'word': 0.4           # Word boundaries
        }
    
    def refine_switch_points(self, text: str, user_languages: Optional[List[str]] = None) -> RefinementResult:
        """Refine switch points in text using linguistic analysis.
        
        Args:
            text: Input text to analyze
            user_languages: Optional list of expected languages
            
        Returns:
            Refined switch point analysis
        """
        print(f"🔍 Refining switch points in text: '{text[:50]}...'")
        
        # Tokenize text
        tokens = self._tokenize_text(text)
        
        if len(tokens) < 2:
            return self._empty_result(text, tokens)
        
        # Detect language for each token/segment
        token_analysis = self._analyze_token_languages(tokens, text, user_languages)
        
        # Find initial switch candidates
        initial_switches = self._find_initial_switches(token_analysis)
        
        # Refine switch points using linguistic features
        refined_switches = self._refine_switches(
            tokens, token_analysis, initial_switches, text
        )
        
        # Perform linguistic analysis
        linguistic_analysis = self._perform_linguistic_analysis(tokens, refined_switches)
        
        result = RefinementResult(
            original_switches=initial_switches,
            refined_switches=refined_switches,
            text=text,
            tokens=tokens,
            token_languages=token_analysis['languages'],
            confidence_scores=token_analysis['confidences'],
            linguistic_analysis=linguistic_analysis
        )
        
        print(f"✓ Refined {len(initial_switches)} → {len(refined_switches)} switch points")
        
        return result
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text preserving important boundaries."""
        # Simple but effective tokenization
        # Split on whitespace but preserve punctuation
        tokens = []
        current_token = ""
        
        for char in text:
            if char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            elif char in string.punctuation:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        return tokens
    
    def _analyze_token_languages(self, tokens: List[str], full_text: str, 
                                user_languages: Optional[List[str]] = None) -> Dict[str, List]:
        """Analyze language for each token using sliding windows."""
        analysis = {
            'languages': [],
            'confidences': [],
            'features': []
        }
        
        # Analyze tokens in overlapping windows
        window_size = 3  # Analyze 3 tokens at a time for better context
        
        for i in range(len(tokens)):
            # Create context window
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(tokens), start_idx + window_size)
            window_tokens = tokens[start_idx:end_idx]
            window_text = ' '.join(window_tokens)
            
            # Skip pure punctuation
            if all(token in string.punctuation for token in window_tokens):
                analysis['languages'].append('unknown')
                analysis['confidences'].append(0.0)
                analysis['features'].append({})
                continue
            
            # Detect language for this window
            result = self.detector.detect_language(window_text, user_languages=user_languages)
            
            # Analyze linguistic features
            token_features = self.linguistic_analyzer.analyze_token_features(
                tokens[i], i, tokens
            )
            
            # Store results
            primary_language = result.detected_languages[0] if result.detected_languages else 'unknown'
            analysis['languages'].append(primary_language)
            analysis['confidences'].append(result.confidence)
            analysis['features'].append(token_features)
        
        return analysis
    
    def _find_initial_switches(self, token_analysis: Dict[str, List]) -> List[int]:
        """Find initial switch point candidates."""
        switches = []
        languages = token_analysis['languages']
        confidences = token_analysis['confidences']
        
        for i in range(1, len(languages)):
            if (languages[i] != languages[i-1] and 
                languages[i] != 'unknown' and 
                languages[i-1] != 'unknown' and
                confidences[i] >= self.min_confidence_threshold):
                switches.append(i)
        
        return switches
    
    def _refine_switches(self, tokens: List[str], token_analysis: Dict[str, List], 
                        initial_switches: List[int], full_text: str) -> List[SwitchPoint]:
        """Refine switch points using linguistic analysis."""
        refined_switches = []
        
        for switch_idx in initial_switches:
            if switch_idx >= len(tokens):
                continue
            
            # Analyze the switch context
            refined_switch = self._analyze_switch_context(
                tokens, token_analysis, switch_idx, full_text
            )
            
            if refined_switch:
                refined_switches.append(refined_switch)
        
        return refined_switches
    
    def _analyze_switch_context(self, tokens: List[str], token_analysis: Dict[str, List], 
                               switch_idx: int, full_text: str) -> Optional[SwitchPoint]:
        """Analyze context around a switch point to refine its position."""
        if switch_idx <= 0 or switch_idx >= len(tokens):
            return None
        
        languages = token_analysis['languages']
        confidences = token_analysis['confidences']
        features = token_analysis['features']
        
        # Determine optimal boundary type
        boundary_type = self._determine_boundary_type(tokens, switch_idx, features)
        
        # Calculate refined position (character position in text)
        char_position = self._calculate_character_position(tokens, switch_idx, full_text)
        
        # Calculate context
        context_start = max(0, switch_idx - self.context_window)
        context_end = min(len(tokens), switch_idx + self.context_window)
        
        context_before = ' '.join(tokens[context_start:switch_idx])
        context_after = ' '.join(tokens[switch_idx:context_end])
        
        # Calculate refined confidence
        refined_confidence = self._calculate_refined_confidence(
            tokens, token_analysis, switch_idx, boundary_type
        )
        
        # Extract linguistic features at switch point
        switch_features = {
            'token_before': tokens[switch_idx - 1] if switch_idx > 0 else '',
            'token_after': tokens[switch_idx] if switch_idx < len(tokens) else '',
            'boundary_score': self.boundary_preferences.get(boundary_type, 0.5),
            'local_coherence': self.linguistic_analyzer.analyze_context_coherence(
                tokens, context_start, context_end
            )
        }
        
        return SwitchPoint(
            position=char_position,
            confidence=refined_confidence,
            from_language=languages[switch_idx - 1] if switch_idx > 0 else 'unknown',
            to_language=languages[switch_idx] if switch_idx < len(languages) else 'unknown',
            linguistic_features=switch_features,
            boundary_type=boundary_type,
            context_before=context_before,
            context_after=context_after
        )
    
    def _determine_boundary_type(self, tokens: List[str], switch_idx: int, 
                                features: List[Dict]) -> str:
        """Determine the type of boundary at the switch point."""
        if switch_idx <= 0 or switch_idx >= len(tokens):
            return 'word'
        
        token_before = tokens[switch_idx - 1] if switch_idx > 0 else ''
        token_current = tokens[switch_idx] if switch_idx < len(tokens) else ''
        
        # Check for sentence boundaries
        if (token_before.endswith('.') or token_before.endswith('!') or 
            token_before.endswith('?') or 
            (switch_idx < len(features) and features[switch_idx].get('is_sentence_start', False))):
            return 'sentence'
        
        # Check for punctuation boundaries
        if token_before in string.punctuation or token_current in string.punctuation:
            return 'punctuation'
        
        # Check for phrase boundaries (simplified)
        if (switch_idx < len(features) and 
            (features[switch_idx].get('is_capitalized', False) or
             token_current.lower() in ['and', 'but', 'or', 'y', 'pero', 'o', 'et', 'mais', 'ou'])):
            return 'phrase'
        
        return 'word'
    
    def _calculate_character_position(self, tokens: List[str], switch_idx: int, full_text: str) -> int:
        """Calculate character position of switch point in original text."""
        # Simple approximation - find position of token in text
        if switch_idx <= 0:
            return 0
        
        # Reconstruct text up to switch point
        prefix_tokens = tokens[:switch_idx]
        prefix_text = ' '.join(prefix_tokens)
        
        # Find this position in original text (approximation)
        position = full_text.find(prefix_text)
        if position >= 0:
            return position + len(prefix_text)
        
        # Fallback: character-based approximation
        char_count = 0
        for i, token in enumerate(tokens):
            if i >= switch_idx:
                break
            char_count += len(token) + 1  # +1 for space
        
        return min(char_count, len(full_text))
    
    def _calculate_refined_confidence(self, tokens: List[str], token_analysis: Dict[str, List], 
                                    switch_idx: int, boundary_type: str) -> float:
        """Calculate refined confidence score for switch point."""
        if switch_idx <= 0 or switch_idx >= len(token_analysis['confidences']):
            return 0.0
        
        # Base confidence from detection
        base_confidence = token_analysis['confidences'][switch_idx]
        
        # Boundary type modifier
        boundary_modifier = self.boundary_preferences.get(boundary_type, 0.5)
        
        # Context coherence
        context_start = max(0, switch_idx - 2)
        context_end = min(len(tokens), switch_idx + 2)
        coherence = self.linguistic_analyzer.analyze_context_coherence(
            tokens, context_start, context_end
        )
        
        # Language indicator strength
        features = token_analysis['features']
        lang_strength = 0.0
        if switch_idx < len(features):
            lang_indicators = features[switch_idx].get('language_indicators', {})
            if lang_indicators:
                lang_strength = max(lang_indicators.values()) / 10.0  # Normalize
        
        # Combine factors
        refined_confidence = (
            base_confidence * 0.5 +           # Base detection confidence
            boundary_modifier * 0.3 +         # Boundary type preference
            coherence * 0.1 +                 # Context coherence
            lang_strength * 0.1               # Language indicator strength
        )
        
        return min(refined_confidence, 1.0)
    
    def _perform_linguistic_analysis(self, tokens: List[str], 
                                   switches: List[SwitchPoint]) -> Dict[str, Any]:
        """Perform overall linguistic analysis of the text."""
        analysis = {
            'total_tokens': len(tokens),
            'switch_density': len(switches) / len(tokens) if tokens else 0,
            'boundary_type_distribution': defaultdict(int),
            'average_confidence': 0.0,
            'language_transitions': defaultdict(int)
        }
        
        # Analyze switches
        if switches:
            for switch in switches:
                analysis['boundary_type_distribution'][switch.boundary_type] += 1
                transition = f"{switch.from_language}→{switch.to_language}"
                analysis['language_transitions'][transition] += 1
            
            analysis['average_confidence'] = np.mean([s.confidence for s in switches])
            analysis['boundary_type_distribution'] = dict(analysis['boundary_type_distribution'])
            analysis['language_transitions'] = dict(analysis['language_transitions'])
        
        return analysis
    
    def _empty_result(self, text: str, tokens: List[str]) -> RefinementResult:
        """Return empty result for texts with no switches."""
        return RefinementResult(
            original_switches=[],
            refined_switches=[],
            text=text,
            tokens=tokens,
            token_languages=[],
            confidence_scores=[],
            linguistic_analysis={}
        )


def main():
    """Example usage of switch point refinement."""
    print("🔬 Switch Point Refinement Example")
    print("=" * 40)
    
    # Initialize refiner
    refiner = SwitchPointRefiner()
    
    # Test cases
    test_texts = [
        "Hello, ¿cómo estás? I am doing bien today!",
        "Je suis très tired aujourd'hui. Need some rest.",
        "Work is trabajo. But I enjoy mi job very much.",
        "¡Perfecto! That sounds really good to me.",
        "Meeting starts at 3pm. La reunión is important."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Text: '{text}'")
        
        # Refine switch points
        result = refiner.refine_switch_points(text, user_languages=['english', 'spanish'])
        
        print(f"Original switches: {len(result.original_switches)}")
        print(f"Refined switches: {len(result.refined_switches)}")
        
        # Show refined switches
        for j, switch in enumerate(result.refined_switches):
            print(f"  {j+1}. {switch.from_language} → {switch.to_language} "
                  f"at pos {switch.position} ({switch.boundary_type}, {switch.confidence:.3f})")
    
    print("\n✓ Switch point refinement example completed")


if __name__ == "__main__":
    main()