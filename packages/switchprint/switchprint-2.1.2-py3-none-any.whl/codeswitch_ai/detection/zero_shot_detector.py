#!/usr/bin/env python3
"""Zero-shot language detection for new languages without retraining."""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import json
import pickle
from pathlib import Path
import re
from collections import defaultdict, Counter
import unicodedata
import os
from urllib.request import urlretrieve

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import fasttext
    FASTTEXT_AVAILABLE = True
except ImportError:
    FASTTEXT_AVAILABLE = False

from .language_detector import DetectionResult


@dataclass
class ZeroShotResult:
    """Result from zero-shot language detection."""
    detected_language: str
    confidence: float
    similarity_scores: Dict[str, float]
    script_analysis: Dict[str, Any]
    linguistic_features: Dict[str, float]
    method_used: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ScriptAnalyzer:
    """Analyze text scripts for zero-shot detection."""
    
    # Unicode script ranges for major writing systems
    SCRIPT_RANGES = {
        'latin': [(0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x00FF), 
                  (0x0100, 0x017F), (0x0180, 0x024F)],
        'cyrillic': [(0x0400, 0x04FF), (0x0500, 0x052F)],
        'arabic': [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)],
        'devanagari': [(0x0900, 0x097F)],
        'chinese': [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],
        'japanese': [(0x3040, 0x309F), (0x30A0, 0x30FF), (0x31F0, 0x31FF)],
        'korean': [(0xAC00, 0xD7AF), (0x1100, 0x11FF), (0x3130, 0x318F)],
        'thai': [(0x0E00, 0x0E7F)],
        'hebrew': [(0x0590, 0x05FF)],
        'greek': [(0x0370, 0x03FF)],
        'armenian': [(0x0530, 0x058F)],
        'georgian': [(0x10A0, 0x10FF)],
    }
    
    # Language families and their typical scripts
    LANGUAGE_FAMILIES = {
        'indo_european': {
            'germanic': ['latin'],
            'romance': ['latin'],
            'slavic': ['latin', 'cyrillic'],
            'indo_iranian': ['arabic', 'devanagari'],
            'greek': ['greek'],
            'armenian': ['armenian']
        },
        'sino_tibetan': {
            'chinese': ['chinese'],
            'tibetan': ['tibetan']
        },
        'japanese': {
            'japanese': ['japanese', 'latin']
        },
        'korean': {
            'korean': ['korean', 'latin']
        },
        'afro_asiatic': {
            'semitic': ['arabic', 'hebrew'],
            'berber': ['latin', 'arabic']
        },
        'niger_congo': {
            'bantu': ['latin'],
            'west_african': ['latin']
        },
        'austronesian': {
            'malayo_polynesian': ['latin'],
            'oceanic': ['latin']
        },
        'tai_kadai': {
            'tai': ['thai', 'latin']
        }
    }
    
    def analyze_script(self, text: str) -> Dict[str, Any]:
        """Analyze script composition of text.
        
        Args:
            text: Input text
            
        Returns:
            Script analysis results
        """
        if not text:
            return {'dominant_script': 'unknown', 'script_distribution': {}, 'confidence': 0.0}
        
        # Count characters by script
        script_counts = defaultdict(int)
        total_chars = 0
        
        for char in text:
            if char.isalpha():
                char_code = ord(char)
                script_found = False
                
                for script_name, ranges in self.SCRIPT_RANGES.items():
                    for start, end in ranges:
                        if start <= char_code <= end:
                            script_counts[script_name] += 1
                            script_found = True
                            break
                    if script_found:
                        break
                
                if not script_found:
                    script_counts['unknown'] += 1
                
                total_chars += 1
        
        if total_chars == 0:
            return {'dominant_script': 'unknown', 'script_distribution': {}, 'confidence': 0.0}
        
        # Calculate script distribution
        script_distribution = {
            script: count / total_chars 
            for script, count in script_counts.items()
        }
        
        # Find dominant script
        dominant_script = max(script_distribution.keys(), key=lambda x: script_distribution[x])
        confidence = script_distribution[dominant_script]
        
        return {
            'dominant_script': dominant_script,
            'script_distribution': script_distribution,
            'confidence': confidence,
            'total_chars': total_chars,
            'script_diversity': len([s for s in script_distribution.values() if s > 0.1])
        }


class LinguisticFeatureExtractor:
    """Extract linguistic features for zero-shot detection."""
    
    # Common patterns in different language families
    LINGUISTIC_PATTERNS = {
        'vowel_patterns': {
            'high_vowels': r'[iuɨ]',
            'low_vowels': r'[aæɑ]',
            'rounded_vowels': r'[uoɔ]'
        },
        'consonant_clusters': {
            'initial_clusters': r'\b[ptkbdgfvszʃʒ]{2,}',
            'final_clusters': r'[ptkbdgfvszʃʒ]{2,}\b',
            'complex_clusters': r'[ptkbdgfvszʃʒ]{3,}'
        },
        'morphological': {
            'agglutination': r'\w{8,}',  # Long words suggest agglutination
            'inflection': r'\w+(ed|ing|s|er|est)\b',  # English-like inflection
            'compounding': r'\b\w+\w+\b'  # Compound-like structures
        }
    }
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """Extract linguistic features from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of linguistic features
        """
        if not text:
            return {}
        
        features = {}
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return features
        
        # Character-level features
        features['avg_word_length'] = np.mean([len(word) for word in words])
        features['max_word_length'] = max([len(word) for word in words])
        features['long_word_ratio'] = len([w for w in words if len(w) > 8]) / len(words)
        
        # Vowel/consonant ratios
        all_chars = ''.join(words)
        vowels = len(re.findall(r'[aeiouäöüáéíóúàèìòùâêîôû]', all_chars))
        consonants = len(re.findall(r'[bcdfghjklmnpqrstvwxyzç]', all_chars))
        total_alpha = vowels + consonants
        
        if total_alpha > 0:
            features['vowel_ratio'] = vowels / total_alpha
            features['consonant_ratio'] = consonants / total_alpha
        else:
            features['vowel_ratio'] = 0.0
            features['consonant_ratio'] = 0.0
        
        # Morphological complexity
        features['morphological_complexity'] = self._calculate_morphological_complexity(words)
        
        # Phonotactic patterns
        features['cluster_density'] = self._calculate_cluster_density(text_lower)
        
        # Repetition patterns
        features['repetition_score'] = self._calculate_repetition_score(words)
        
        # Word order indicators (basic)
        features['word_order_score'] = self._calculate_word_order_score(text)
        
        return features
    
    def _calculate_morphological_complexity(self, words: List[str]) -> float:
        """Calculate morphological complexity score."""
        if not words:
            return 0.0
        
        # Look for affixation patterns
        prefix_patterns = ['un', 're', 'pre', 'dis', 'over', 'under']
        suffix_patterns = ['ed', 'ing', 'ly', 'tion', 'ness', 'ment', 'able']
        
        affixed_words = 0
        for word in words:
            if len(word) > 4:
                has_prefix = any(word.startswith(prefix) for prefix in prefix_patterns)
                has_suffix = any(word.endswith(suffix) for suffix in suffix_patterns)
                if has_prefix or has_suffix:
                    affixed_words += 1
        
        return affixed_words / len(words)
    
    def _calculate_cluster_density(self, text: str) -> float:
        """Calculate consonant cluster density."""
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{2,}', text)
        words = re.findall(r'\b\w+\b', text)
        
        if not words:
            return 0.0
        
        return len(consonant_clusters) / len(words)
    
    def _calculate_repetition_score(self, words: List[str]) -> float:
        """Calculate repetition pattern score."""
        if len(words) < 2:
            return 0.0
        
        word_counts = Counter(words)
        repeated_words = sum(1 for count in word_counts.values() if count > 1)
        
        return repeated_words / len(set(words))
    
    def _calculate_word_order_score(self, text: str) -> float:
        """Calculate basic word order indicators."""
        # Very simple heuristics for word order
        sentences = re.split(r'[.!?]', text)
        
        if not sentences:
            return 0.5  # Neutral
        
        # Look for common word order patterns
        sov_indicators = len(re.findall(r'\w+\s+\w+\s+(is|are|was|were)\b', text, re.IGNORECASE))
        svo_indicators = len(re.findall(r'\b(is|are|was|were)\s+\w+\s+\w+', text, re.IGNORECASE))
        
        total_indicators = sov_indicators + svo_indicators
        if total_indicators == 0:
            return 0.5
        
        return svo_indicators / total_indicators  # Higher = more SVO-like


class ZeroShotLanguageDetector:
    """Zero-shot language detector using multiple strategies."""
    
    def __init__(self, embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2", 
                 load_embedding_model: bool = False):
        """Initialize zero-shot detector.
        
        Args:
            embedding_model: Sentence transformer model for embeddings
            load_embedding_model: Whether to load embedding model (slower startup)
        """
        self.script_analyzer = ScriptAnalyzer()
        self.feature_extractor = LinguisticFeatureExtractor()
        
        # Initialize embedding model if available and requested
        self.embedding_model = None
        if load_embedding_model and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                print(f"✓ Loaded embedding model: {embedding_model}")
            except Exception as e:
                print(f"⚠ Failed to load embedding model: {e}")
        
        # Known language profiles (small set for bootstrapping)
        self.language_profiles = self._initialize_language_profiles()
    

class ZeroShotLanguageDetector:
    # ... (rest of the class)
    def __init__(self, embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2", 
                 load_embedding_model: bool = False):
        """Initialize zero-shot detector.
        
        Args:
            embedding_model: Sentence transformer model for embeddings
            load_embedding_model: Whether to load embedding model (slower startup)
        """
        self.script_analyzer = ScriptAnalyzer()
        self.feature_extractor = LinguisticFeatureExtractor()
        
        # Initialize embedding model if available and requested
        self.embedding_model = None
        if load_embedding_model and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                print(f"✓ Loaded embedding model: {embedding_model}")
            except Exception as e:
                print(f"⚠ Failed to load embedding model: {e}")
        
        # Known language profiles (small set for bootstrapping)
        self.language_profiles = self._initialize_language_profiles()
        
        # FastText model for fallback
        self.fasttext_model = None
        if FASTTEXT_AVAILABLE:
            try:
                # Try to load pre-trained FastText model (if available)
                model_path = self._download_default_fasttext_model()
                self.fasttext_model = fasttext.load_model(model_path)
                print("✓ Loaded FastText language identification model")
            except Exception as e:
                print(f"⚠ FastText pre-trained model not available: {e}")

    def _download_default_fasttext_model(self) -> str:
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
    
    def _initialize_language_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize basic language profiles for zero-shot detection."""
        # Basic profiles based on linguistic knowledge
        profiles = {
            'english': {
                'scripts': ['latin'],
                'linguistic_features': {
                    'avg_word_length': 4.5,
                    'vowel_ratio': 0.38,
                    'morphological_complexity': 0.2,
                    'cluster_density': 0.15
                },
                'family': 'indo_european.germanic'
            },
            'spanish': {
                'scripts': ['latin'],
                'linguistic_features': {
                    'avg_word_length': 5.2,
                    'vowel_ratio': 0.42,
                    'morphological_complexity': 0.35,
                    'cluster_density': 0.08
                },
                'family': 'indo_european.romance'
            },
            'french': {
                'scripts': ['latin'],
                'linguistic_features': {
                    'avg_word_length': 5.8,
                    'vowel_ratio': 0.44,
                    'morphological_complexity': 0.25,
                    'cluster_density': 0.12
                },
                'family': 'indo_european.romance'
            },
            'german': {
                'scripts': ['latin'],
                'linguistic_features': {
                    'avg_word_length': 6.1,
                    'vowel_ratio': 0.35,
                    'morphological_complexity': 0.45,
                    'cluster_density': 0.22
                },
                'family': 'indo_european.germanic'
            },
            'chinese': {
                'scripts': ['chinese'],
                'linguistic_features': {
                    'avg_word_length': 2.1,
                    'vowel_ratio': 0.25,
                    'morphological_complexity': 0.05,
                    'cluster_density': 0.02
                },
                'family': 'sino_tibetan.chinese'
            },
            'arabic': {
                'scripts': ['arabic'],
                'linguistic_features': {
                    'avg_word_length': 4.8,
                    'vowel_ratio': 0.28,
                    'morphological_complexity': 0.65,
                    'cluster_density': 0.18
                },
                'family': 'afro_asiatic.semitic'
            },
            'russian': {
                'scripts': ['cyrillic'],
                'linguistic_features': {
                    'avg_word_length': 5.9,
                    'vowel_ratio': 0.32,
                    'morphological_complexity': 0.55,
                    'cluster_density': 0.25
                },
                'family': 'indo_european.slavic'
            },
            'japanese': {
                'scripts': ['japanese', 'latin'],
                'linguistic_features': {
                    'avg_word_length': 3.2,
                    'vowel_ratio': 0.48,
                    'morphological_complexity': 0.15,
                    'cluster_density': 0.05
                },
                'family': 'japanese.japanese'
            }
        }
        
        return profiles
    
    def detect_language(self, text: str, candidate_languages: Optional[List[str]] = None) -> ZeroShotResult:
        """Detect language using zero-shot methods.
        
        Args:
            text: Input text
            candidate_languages: Optional list of candidate languages to consider
            
        Returns:
            Zero-shot detection result
        """
        if not text or not text.strip():
            return ZeroShotResult(
                detected_language='unknown',
                confidence=0.0,
                similarity_scores={},
                script_analysis={},
                linguistic_features={},
                method_used='none'
            )
        
        # Analyze scripts
        script_analysis = self.script_analyzer.analyze_script(text)
        
        # Extract linguistic features
        linguistic_features = self.feature_extractor.extract_features(text)
        
        # Try different detection methods
        methods = []
        
        # Method 1: Script-based detection
        if script_analysis['confidence'] > 0.8:
            script_result = self._detect_by_script(script_analysis, candidate_languages)
            methods.append(('script', script_result))
        
        # Method 2: Linguistic feature matching
        if linguistic_features:
            feature_result = self._detect_by_features(linguistic_features, candidate_languages)
            methods.append(('features', feature_result))
        
        # Method 3: Embedding similarity (if available)
        if self.embedding_model:
            embedding_result = self._detect_by_embeddings(text, candidate_languages)
            methods.append(('embeddings', embedding_result))
        
        # Method 4: FastText fallback (if available)
        if self.fasttext_model:
            fasttext_result = self._detect_by_fasttext(text)
            methods.append(('fasttext', fasttext_result))
        
        # Combine results
        if methods:
            final_result = self._combine_method_results(methods)
        else:
            final_result = ZeroShotResult(
                detected_language='unknown',
                confidence=0.0,
                similarity_scores={},
                script_analysis=script_analysis,
                linguistic_features=linguistic_features,
                method_used='none'
            )
        
        # Update with analysis results
        final_result.script_analysis = script_analysis
        final_result.linguistic_features = linguistic_features
        
        return final_result
    
    def _detect_by_script(self, script_analysis: Dict[str, Any], 
                         candidate_languages: Optional[List[str]] = None) -> Tuple[str, float, Dict[str, float]]:
        """Detect language based on script analysis."""
        dominant_script = script_analysis['dominant_script']
        
        # Find languages that use this script
        matching_languages = []
        for lang, profile in self.language_profiles.items():
            if candidate_languages and lang not in candidate_languages:
                continue
            if dominant_script in profile['scripts']:
                matching_languages.append(lang)
        
        if not matching_languages:
            return 'unknown', 0.0, {}
        
        # If only one language matches, return it with high confidence
        if len(matching_languages) == 1:
            confidence = min(script_analysis['confidence'] * 0.9, 0.95)
            return matching_languages[0], confidence, {matching_languages[0]: confidence}
        
        # Multiple languages - use additional heuristics
        scores = {}
        for lang in matching_languages:
            # Base score from script confidence
            score = script_analysis['confidence'] * 0.7
            
            # Adjust based on script exclusivity
            exclusive_scripts = ['chinese', 'arabic', 'japanese', 'korean', 'thai']
            if dominant_script in exclusive_scripts:
                score *= 1.2
            
            scores[lang] = min(score, 0.95)
        
        best_lang = max(scores.keys(), key=lambda x: scores[x])
        return best_lang, scores[best_lang], scores
    
    def _detect_by_features(self, linguistic_features: Dict[str, float], 
                           candidate_languages: Optional[List[str]] = None) -> Tuple[str, float, Dict[str, float]]:
        """Detect language based on linguistic features."""
        scores = {}
        
        for lang, profile in self.language_profiles.items():
            if candidate_languages and lang not in candidate_languages:
                continue
            
            # Calculate feature similarity
            profile_features = profile['linguistic_features']
            similarity = self._calculate_feature_similarity(linguistic_features, profile_features)
            scores[lang] = similarity
        
        if not scores:
            return 'unknown', 0.0, {}
        
        best_lang = max(scores.keys(), key=lambda x: scores[x])
        confidence = scores[best_lang]
        
        return best_lang, confidence, scores
    
    def _calculate_feature_similarity(self, features1: Dict[str, float], 
                                    features2: Dict[str, float]) -> float:
        """Calculate similarity between feature vectors."""
        common_features = set(features1.keys()) & set(features2.keys())
        
        if not common_features:
            return 0.0
        
        # Calculate normalized distance
        distances = []
        for feature in common_features:
            val1 = features1[feature]
            val2 = features2[feature]
            
            # Normalize distance based on feature type
            if feature == 'avg_word_length':
                max_diff = 10.0  # Max reasonable word length difference
            elif feature in ['vowel_ratio', 'consonant_ratio']:
                max_diff = 1.0   # Ratio differences
            else:
                max_diff = 1.0   # Default normalization
            
            distance = abs(val1 - val2) / max_diff
            distances.append(min(distance, 1.0))
        
        # Convert average distance to similarity
        avg_distance = np.mean(distances)
        similarity = 1.0 - avg_distance
        
        return max(similarity, 0.0)
    
    def _detect_by_embeddings(self, text: str, 
                             candidate_languages: Optional[List[str]] = None) -> Tuple[str, float, Dict[str, float]]:
        """Detect language using sentence embeddings."""
        if not self.embedding_model:
            return 'unknown', 0.0, {}
        
        try:
            # Get text embedding
            text_embedding = self.embedding_model.encode([text])[0]
            
            # Compare with language exemplars (if we had them)
            # For now, return low confidence
            return 'unknown', 0.3, {}
            
        except Exception as e:
            print(f"⚠ Embedding detection failed: {e}")
            return 'unknown', 0.0, {}
    
    def _detect_by_fasttext(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """Detect language using FastText."""
        if not self.fasttext_model:
            return 'unknown', 0.0, {}
        
        try:
            # Clean text for FastText
            clean_text = re.sub(r'\n+', ' ', text.strip())
            
            # Predict language
            predictions = self.fasttext_model.predict(clean_text, k=5)
            labels, scores = predictions
            
            # Convert FastText labels to language names
            lang_scores = {}
            for label, score in zip(labels, scores):
                # FastText labels are like '__label__en'
                lang_code = label.replace('__label__', '')
                
                # Map common codes to language names
                lang_map = {
                    'en': 'english', 'es': 'spanish', 'fr': 'french', 
                    'de': 'german', 'zh': 'chinese', 'ar': 'arabic',
                    'ru': 'russian', 'ja': 'japanese', 'ko': 'korean'
                }
                
                lang_name = lang_map.get(lang_code, lang_code)
                lang_scores[lang_name] = float(score)
            
            if lang_scores:
                best_lang = max(lang_scores.keys(), key=lambda x: lang_scores[x])
                confidence = lang_scores[best_lang]
                return best_lang, confidence, lang_scores
            
        except Exception as e:
            print(f"⚠ FastText detection failed: {e}")
        
        return 'unknown', 0.0, {}
    
    def _combine_method_results(self, method_results: List[Tuple[str, Tuple[str, float, Dict[str, float]]]]) -> ZeroShotResult:
        """Combine results from multiple detection methods."""
        if not method_results:
            return ZeroShotResult(
                detected_language='unknown',
                confidence=0.0,
                similarity_scores={},
                script_analysis={},
                linguistic_features={},
                method_used='none'
            )
        
        # Weight different methods
        method_weights = {
            'script': 0.4,
            'features': 0.3,
            'embeddings': 0.2,
            'fasttext': 0.1
        }
        
        # Aggregate scores
        aggregated_scores = defaultdict(float)
        total_weight = 0.0
        methods_used = []
        
        for method_name, (detected_lang, confidence, scores) in method_results:
            weight = method_weights.get(method_name, 0.1)
            total_weight += weight
            methods_used.append(method_name)
            
            for lang, score in scores.items():
                aggregated_scores[lang] += score * weight
        
        # Normalize scores
        if total_weight > 0:
            for lang in aggregated_scores:
                aggregated_scores[lang] /= total_weight
        
        # Find best language
        if aggregated_scores:
            best_language = max(aggregated_scores.keys(), key=lambda x: aggregated_scores[x])
            final_confidence = aggregated_scores[best_language]
            
            # Boost confidence if multiple methods agree
            agreement_boost = len([
                result for _, result in method_results 
                if result[0] == best_language and result[1] > 0.5
            ]) / len(method_results)
            
            final_confidence = min(final_confidence * (1 + agreement_boost * 0.2), 0.95)
        else:
            best_language = 'unknown'
            final_confidence = 0.0
        
        return ZeroShotResult(
            detected_language=best_language,
            confidence=final_confidence,
            similarity_scores=dict(aggregated_scores),
            script_analysis={},
            linguistic_features={},
            method_used='+'.join(methods_used)
        )
    
    def add_language_profile(self, language: str, profile: Dict[str, Any]) -> None:
        """Add a new language profile for future detection.
        
        Args:
            language: Language name
            profile: Language profile with scripts and features
        """
        self.language_profiles[language] = profile
        print(f"✓ Added profile for {language}")
    
    def learn_from_examples(self, examples: List[Tuple[str, str]]) -> None:
        """Learn language profiles from labeled examples.
        
        Args:
            examples: List of (text, language) pairs
        """
        language_texts = defaultdict(list)
        
        # Group texts by language
        for text, language in examples:
            language_texts[language].append(text)
        
        # Extract profiles for each language
        for language, texts in language_texts.items():
            if len(texts) < 3:
                continue  # Need minimum examples
            
            # Aggregate script analysis
            script_analyses = [self.script_analyzer.analyze_script(text) for text in texts]
            dominant_scripts = [analysis['dominant_script'] for analysis in script_analyses]
            common_scripts = list(set(dominant_scripts))
            
            # Aggregate linguistic features
            feature_sets = [self.feature_extractor.extract_features(text) for text in texts]
            
            if feature_sets and all(features for features in feature_sets):
                # Average features
                avg_features = {}
                feature_keys = set().union(*[f.keys() for f in feature_sets])
                
                for key in feature_keys:
                    values = [f.get(key, 0) for f in feature_sets if key in f]
                    if values:
                        avg_features[key] = np.mean(values)
                
                # Create profile
                profile = {
                    'scripts': common_scripts,
                    'linguistic_features': avg_features,
                    'family': 'learned',
                    'example_count': len(texts)
                }
                
                self.add_language_profile(language, profile)
                print(f"✓ Learned profile for {language} from {len(texts)} examples")


def main():
    """Example usage of zero-shot language detection."""
    print("🔬 Zero-shot Language Detection Example")
    print("=" * 40)
    
    # Initialize detector
    detector = ZeroShotLanguageDetector()
    
    # Test cases for different languages and scripts
    test_cases = [
        ("Hello, how are you today?", "english"),
        ("Hola, ¿cómo estás hoy?", "spanish"),
        ("Bonjour, comment allez-vous?", "french"),
        ("Guten Tag, wie geht es Ihnen?", "german"),
        ("Привет, как дела?", "russian"),
        ("你好，你好吗？", "chinese"),
        ("مرحبا، كيف حالك؟", "arabic"),
        ("こんにちは、元気ですか？", "japanese"),
        ("안녕하세요, 어떻게 지내세요?", "korean"),
        ("Mixed English and español text", "unknown"),
    ]
    
    print("\n🧪 Testing zero-shot detection:")
    print("-" * 30)
    
    for text, expected in test_cases:
        result = detector.detect_language(text)
        
        print(f"\nText: '{text}'")
        print(f"Expected: {expected}")
        print(f"Detected: {result.detected_language} (confidence: {result.confidence:.3f})")
        print(f"Method: {result.method_used}")
        
        if result.script_analysis:
            dominant_script = result.script_analysis.get('dominant_script', 'unknown')
            print(f"Script: {dominant_script}")
        
        # Show top 3 candidates
        if result.similarity_scores:
            top_candidates = sorted(
                result.similarity_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            print(f"Top candidates: {dict(top_candidates)}")
    
    print("\n✓ Zero-shot detection example completed")


if __name__ == "__main__":
    main()