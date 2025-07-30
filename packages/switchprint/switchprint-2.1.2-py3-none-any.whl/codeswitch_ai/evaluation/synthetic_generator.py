#!/usr/bin/env python3
"""Synthetic multilingual dataset generation for controlled evaluation."""

import os
import json
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import itertools
from collections import defaultdict

try:
    from ..detection.ensemble_detector import EnsembleDetector
    from ..detection.fasttext_detector import FastTextDetector
    from ..detection.transformer_detector import TransformerDetector
    DETECTORS_AVAILABLE = True
except ImportError:
    DETECTORS_AVAILABLE = False


@dataclass
class SyntheticDataConfig:
    """Configuration for synthetic data generation."""
    languages: List[str]
    sample_count: int
    code_mixing_ratio: float
    switch_patterns: List[str]
    domains: List[str]
    difficulty_levels: List[str]
    include_edge_cases: bool
    include_romanization: bool
    include_social_media: bool
    seed: Optional[int] = 42
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SyntheticSample:
    """Represents a synthetic code-mixed sample."""
    text: str
    languages: List[str]
    switch_points: List[int]
    ground_truth_labels: List[str]  # Token-level labels
    confidence_expected: float
    difficulty_level: str
    domain: str
    pattern_type: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SyntheticDataGenerator:
    """Generate synthetic multilingual code-switching datasets."""
    
    # Language-specific vocabulary and patterns
    VOCABULARIES = {
        'english': {
            'common': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with', 'for', 'as', 'was', 'on', 'are'],
            'greetings': ['hello', 'hi', 'good morning', 'good evening', 'how are you', 'nice to meet you'],
            'everyday': ['today', 'tomorrow', 'yesterday', 'work', 'home', 'family', 'friend', 'food', 'water', 'time'],
            'social': ['awesome', 'cool', 'amazing', 'perfect', 'great', 'wonderful', 'fantastic', 'excellent'],
            'connectors': ['but', 'and', 'or', 'so', 'because', 'although', 'however', 'therefore'],
            'questions': ['what', 'when', 'where', 'why', 'how', 'who', 'which'],
            'numbers': ['one', 'two', 'three', 'first', 'second', 'last', 'many', 'few', 'some', 'all']
        },
        'spanish': {
            'common': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'te', 'lo', 'le', 'da'],
            'greetings': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', '¿cómo estás?', 'mucho gusto'],
            'everyday': ['hoy', 'mañana', 'ayer', 'trabajo', 'casa', 'familia', 'amigo', 'comida', 'agua', 'tiempo'],
            'social': ['genial', 'increíble', 'perfecto', 'excelente', 'fantástico', 'maravilloso', 'súper'],
            'connectors': ['pero', 'y', 'o', 'así que', 'porque', 'aunque', 'sin embargo', 'por lo tanto'],
            'questions': ['qué', 'cuándo', 'dónde', 'por qué', 'cómo', 'quién', 'cuál'],
            'numbers': ['uno', 'dos', 'tres', 'primero', 'segundo', 'último', 'muchos', 'pocos', 'algunos', 'todos']
        },
        'hindi': {
            'common': ['hai', 'ka', 'ki', 'ke', 'ko', 'se', 'me', 'aur', 'ya', 'to', 'jo', 'wo', 'ye', 'is'],
            'greetings': ['namaste', 'namaskar', 'sat sri akal', 'aadab', 'kaise hain', 'kya haal hai'],
            'everyday': ['aaj', 'kal', 'ghar', 'kaam', 'parivaar', 'dost', 'khana', 'paani', 'samay', 'shahar'],
            'social': ['accha', 'bahut accha', 'zabardast', 'kamaal', 'shandar', 'behtareen', 'mast'],
            'connectors': ['lekin', 'aur', 'ya', 'kyunki', 'agar', 'phir', 'isliye', 'jabki'],
            'questions': ['kya', 'kab', 'kahan', 'kyun', 'kaise', 'kaun', 'konsa'],
            'numbers': ['ek', 'do', 'teen', 'pehla', 'doosra', 'aakhri', 'bahut', 'kuch', 'sab', 'kai']
        },
        'french': {
            'common': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce'],
            'greetings': ['bonjour', 'bonsoir', 'salut', 'comment allez-vous', 'enchanté', 'bonne journée'],
            'everyday': ['aujourd\'hui', 'demain', 'hier', 'travail', 'maison', 'famille', 'ami', 'nourriture', 'eau', 'temps'],
            'social': ['génial', 'incroyable', 'parfait', 'excellent', 'fantastique', 'merveilleux', 'super'],
            'connectors': ['mais', 'et', 'ou', 'donc', 'parce que', 'bien que', 'cependant', 'par conséquent'],
            'questions': ['quoi', 'quand', 'où', 'pourquoi', 'comment', 'qui', 'quel'],
            'numbers': ['un', 'deux', 'trois', 'premier', 'deuxième', 'dernier', 'beaucoup', 'peu', 'quelques', 'tous']
        }
    }
    
    # Code-switching patterns
    SWITCH_PATTERNS = {
        'intersentential': 'Switch between sentences',
        'intrasentential': 'Switch within sentences', 
        'tag_switching': 'Insert tags/expressions',
        'borrowing': 'Borrow individual words',
        'alternating': 'Alternate languages regularly',
        'matrix_embedded': 'Embed phrases in matrix language'
    }
    
    # Domain-specific templates
    DOMAIN_TEMPLATES = {
        'casual_conversation': [
            "{greeting}, {question}?",
            "{social_expr} {everyday_word} {connector} {everyday_word}",
            "{question} {everyday_word} {connector} {social_expr}?"
        ],
        'social_media': [
            "{social_expr}! #{hashtag} {social_expr}",
            "@{username} {question} {social_expr}?",
            "{everyday_word} {social_expr} 😊 #{hashtag}"
        ],
        'work': [
            "{everyday_word} meeting {connector} {everyday_word}",
            "Project {everyday_word} {connector} deadline {everyday_word}",
            "{question} presentation {connector} {everyday_word}?"
        ],
        'education': [
            "{question} homework {connector} {everyday_word}?",
            "Exam {everyday_word} {connector} {social_expr}",
            "Teacher {everyday_word} {connector} student {everyday_word}"
        ],
        'family': [
            "{everyday_word} family {connector} {social_expr}",
            "{question} parents {connector} {everyday_word}?",
            "Children {everyday_word} {connector} {social_expr}"
        ]
    }
    
    def __init__(self, config: SyntheticDataConfig):
        """Initialize synthetic data generator.
        
        Args:
            config: Configuration for data generation
        """
        self.config = config
        
        if config.seed:
            random.seed(config.seed)
            np.random.seed(config.seed)
        
        self.samples = []
        self.statistics = defaultdict(int)
    
    def generate_dataset(self) -> List[SyntheticSample]:
        """Generate complete synthetic dataset.
        
        Returns:
            List of synthetic samples
        """
        print(f"🔧 Generating {self.config.sample_count} synthetic samples...")
        print(f"📊 Languages: {', '.join(self.config.languages)}")
        print(f"🔀 Code-mixing ratio: {self.config.code_mixing_ratio:.1%}")
        
        # Generate samples for each pattern and difficulty combination
        samples_per_combination = self.config.sample_count // (
            len(self.config.switch_patterns) * 
            len(self.config.difficulty_levels) * 
            len(self.config.domains)
        )
        
        for pattern in self.config.switch_patterns:
            for difficulty in self.config.difficulty_levels:
                for domain in self.config.domains:
                    for _ in range(samples_per_combination):
                        sample = self._generate_single_sample(pattern, difficulty, domain)
                        if sample:
                            self.samples.append(sample)
                            self.statistics[f"{pattern}_{difficulty}_{domain}"] += 1
        
        # Fill remaining samples with random combinations
        while len(self.samples) < self.config.sample_count:
            pattern = random.choice(self.config.switch_patterns)
            difficulty = random.choice(self.config.difficulty_levels)
            domain = random.choice(self.config.domains)
            
            sample = self._generate_single_sample(pattern, difficulty, domain)
            if sample:
                self.samples.append(sample)
                self.statistics['random_fill'] += 1
        
        # Add edge cases if requested
        if self.config.include_edge_cases:
            edge_cases = self._generate_edge_cases()
            self.samples.extend(edge_cases)
        
        print(f"✅ Generated {len(self.samples)} synthetic samples")
        self._print_statistics()
        
        return self.samples
    
    def _generate_single_sample(self, pattern: str, difficulty: str, domain: str) -> Optional[SyntheticSample]:
        """Generate a single synthetic sample.
        
        Args:
            pattern: Code-switching pattern to use
            difficulty: Difficulty level ('easy', 'medium', 'hard')
            domain: Domain category
            
        Returns:
            Generated synthetic sample or None if generation failed
        """
        try:
            # Determine if this should be code-mixed or monolingual
            is_code_mixed = random.random() < self.config.code_mixing_ratio
            
            if is_code_mixed and len(self.config.languages) >= 2:
                # Generate code-mixed sample
                return self._generate_code_mixed_sample(pattern, difficulty, domain)
            else:
                # Generate monolingual sample
                language = random.choice(self.config.languages)
                return self._generate_monolingual_sample(language, difficulty, domain)
                
        except Exception as e:
            print(f"⚠️ Error generating sample: {e}")
            return None
    
    def _generate_code_mixed_sample(self, pattern: str, difficulty: str, domain: str) -> SyntheticSample:
        """Generate a code-mixed sample with specific pattern."""
        # Select languages for mixing
        lang1, lang2 = random.sample(self.config.languages, 2)
        
        # Generate text based on pattern
        if pattern == 'intersentential':
            text, labels, switch_points = self._generate_intersentential(lang1, lang2, domain, difficulty)
        elif pattern == 'intrasentential':
            text, labels, switch_points = self._generate_intrasentential(lang1, lang2, domain, difficulty)
        elif pattern == 'tag_switching':
            text, labels, switch_points = self._generate_tag_switching(lang1, lang2, domain, difficulty)
        elif pattern == 'borrowing':
            text, labels, switch_points = self._generate_borrowing(lang1, lang2, domain, difficulty)
        elif pattern == 'alternating':
            text, labels, switch_points = self._generate_alternating(lang1, lang2, domain, difficulty)
        elif pattern == 'matrix_embedded':
            text, labels, switch_points = self._generate_matrix_embedded(lang1, lang2, domain, difficulty)
        else:
            # Default to intrasentential
            text, labels, switch_points = self._generate_intrasentential(lang1, lang2, domain, difficulty)
        
        # Calculate expected confidence based on difficulty
        confidence_map = {'easy': 0.9, 'medium': 0.7, 'hard': 0.5}
        expected_confidence = confidence_map.get(difficulty, 0.7)
        
        # Add some randomness to confidence
        expected_confidence += random.uniform(-0.1, 0.1)
        expected_confidence = max(0.1, min(0.95, expected_confidence))
        
        return SyntheticSample(
            text=text,
            languages=[lang1, lang2],
            switch_points=switch_points,
            ground_truth_labels=labels,
            confidence_expected=expected_confidence,
            difficulty_level=difficulty,
            domain=domain,
            pattern_type=pattern,
            metadata={
                'is_code_mixed': True,
                'primary_language': lang1,
                'secondary_language': lang2,
                'switch_count': len(switch_points),
                'token_count': len(labels)
            }
        )
    
    def _generate_monolingual_sample(self, language: str, difficulty: str, domain: str) -> SyntheticSample:
        """Generate a monolingual sample."""
        vocab = self.VOCABULARIES.get(language, self.VOCABULARIES['english'])
        
        # Generate text of varying length based on difficulty
        length_map = {'easy': (3, 6), 'medium': (7, 12), 'hard': (13, 20)}
        min_len, max_len = length_map.get(difficulty, (7, 12))
        text_length = random.randint(min_len, max_len)
        
        # Select words from appropriate categories
        words = []
        categories = ['common', 'everyday', 'social']
        
        if domain in self.DOMAIN_TEMPLATES:
            template = random.choice(self.DOMAIN_TEMPLATES[domain])
            # Simple template filling (simplified)
            words = random.choices(vocab['common'] + vocab['everyday'], k=text_length)
        else:
            for _ in range(text_length):
                category = random.choice(categories)
                if category in vocab:
                    words.append(random.choice(vocab[category]))
                else:
                    words.append(random.choice(vocab['common']))
        
        text = ' '.join(words)
        labels = [language] * len(words)
        
        # Calculate expected confidence (monolingual should be high)
        confidence_map = {'easy': 0.95, 'medium': 0.85, 'hard': 0.75}
        expected_confidence = confidence_map.get(difficulty, 0.85)
        
        return SyntheticSample(
            text=text,
            languages=[language],
            switch_points=[],
            ground_truth_labels=labels,
            confidence_expected=expected_confidence,
            difficulty_level=difficulty,
            domain=domain,
            pattern_type='monolingual',
            metadata={
                'is_code_mixed': False,
                'primary_language': language,
                'secondary_language': None,
                'switch_count': 0,
                'token_count': len(labels)
            }
        )
    
    def _generate_intersentential(self, lang1: str, lang2: str, domain: str, difficulty: str) -> Tuple[str, List[str], List[int]]:
        """Generate intersentential code-switching (between sentences)."""
        vocab1 = self.VOCABULARIES.get(lang1, self.VOCABULARIES['english'])
        vocab2 = self.VOCABULARIES.get(lang2, self.VOCABULARIES['english'])
        
        # Create two sentences in different languages
        sentence1_words = random.choices(vocab1['common'] + vocab1['everyday'], k=random.randint(3, 7))
        sentence2_words = random.choices(vocab2['common'] + vocab2['everyday'], k=random.randint(3, 7))
        
        # Combine sentences
        all_words = sentence1_words + sentence2_words
        labels = [lang1] * len(sentence1_words) + [lang2] * len(sentence2_words)
        switch_points = [len(sentence1_words)]
        
        text = ' '.join(all_words)
        return text, labels, switch_points
    
    def _generate_intrasentential(self, lang1: str, lang2: str, domain: str, difficulty: str) -> Tuple[str, List[str], List[int]]:
        """Generate intrasentential code-switching (within sentence)."""
        vocab1 = self.VOCABULARIES.get(lang1, self.VOCABULARIES['english'])
        vocab2 = self.VOCABULARIES.get(lang2, self.VOCABULARIES['english'])
        
        # Create mixed sentence with alternating chunks
        words = []
        labels = []
        switch_points = []
        
        total_length = random.randint(6, 15)
        current_lang = lang1
        chunk_size = random.randint(1, 3)
        
        for i in range(total_length):
            vocab = vocab1 if current_lang == lang1 else vocab2
            word = random.choice(vocab['common'] + vocab['everyday'])
            words.append(word)
            labels.append(current_lang)
            
            # Switch language after chunk
            if (i + 1) % chunk_size == 0 and i < total_length - 1:
                switch_points.append(i + 1)
                current_lang = lang2 if current_lang == lang1 else lang1
                chunk_size = random.randint(1, 4)
        
        text = ' '.join(words)
        return text, labels, switch_points
    
    def _generate_tag_switching(self, lang1: str, lang2: str, domain: str, difficulty: str) -> Tuple[str, List[str], List[int]]:
        """Generate tag switching (inserting tags/expressions)."""
        vocab1 = self.VOCABULARIES.get(lang1, self.VOCABULARIES['english'])
        vocab2 = self.VOCABULARIES.get(lang2, self.VOCABULARIES['english'])
        
        # Main sentence in one language
        main_words = random.choices(vocab1['common'] + vocab1['everyday'], k=random.randint(5, 10))
        
        # Insert tag from other language
        tag_position = random.randint(0, len(main_words))
        tag_word = random.choice(vocab2['social'] + vocab2['greetings'])
        
        words = main_words[:tag_position] + [tag_word] + main_words[tag_position:]
        labels = [lang1] * tag_position + [lang2] + [lang1] * (len(main_words) - tag_position)
        switch_points = [tag_position, tag_position + 1] if tag_position < len(main_words) else [tag_position]
        
        text = ' '.join(words)
        return text, labels, switch_points
    
    def _generate_borrowing(self, lang1: str, lang2: str, domain: str, difficulty: str) -> Tuple[str, List[str], List[int]]:
        """Generate borrowing (individual word borrowing)."""
        vocab1 = self.VOCABULARIES.get(lang1, self.VOCABULARIES['english'])
        vocab2 = self.VOCABULARIES.get(lang2, self.VOCABULARIES['english'])
        
        # Sentence mostly in one language with borrowed words
        words = []
        labels = []
        switch_points = []
        
        sentence_length = random.randint(6, 12)
        borrow_count = random.randint(1, 3)
        borrow_positions = random.sample(range(sentence_length), borrow_count)
        
        for i in range(sentence_length):
            if i in borrow_positions:
                # Borrowed word
                word = random.choice(vocab2['everyday'] + vocab2['social'])
                words.append(word)
                labels.append(lang2)
                if i > 0 and labels[i-1] != lang2:
                    switch_points.append(i)
            else:
                # Main language word
                word = random.choice(vocab1['common'] + vocab1['everyday'])
                words.append(word)
                labels.append(lang1)
                if i > 0 and labels[i-1] != lang1:
                    switch_points.append(i)
        
        text = ' '.join(words)
        return text, labels, switch_points
    
    def _generate_alternating(self, lang1: str, lang2: str, domain: str, difficulty: str) -> Tuple[str, List[str], List[int]]:
        """Generate alternating pattern."""
        vocab1 = self.VOCABULARIES.get(lang1, self.VOCABULARIES['english'])
        vocab2 = self.VOCABULARIES.get(lang2, self.VOCABULARIES['english'])
        
        words = []
        labels = []
        switch_points = []
        
        sentence_length = random.randint(8, 16)
        current_lang = lang1
        
        for i in range(sentence_length):
            vocab = vocab1 if current_lang == lang1 else vocab2
            word = random.choice(vocab['common'] + vocab['everyday'])
            words.append(word)
            labels.append(current_lang)
            
            # Alternate every 2-3 words
            if (i + 1) % random.randint(2, 3) == 0:
                if i < sentence_length - 1:
                    switch_points.append(i + 1)
                    current_lang = lang2 if current_lang == lang1 else lang1
        
        text = ' '.join(words)
        return text, labels, switch_points
    
    def _generate_matrix_embedded(self, lang1: str, lang2: str, domain: str, difficulty: str) -> Tuple[str, List[str], List[int]]:
        """Generate matrix-embedded pattern."""
        vocab1 = self.VOCABULARIES.get(lang1, self.VOCABULARIES['english'])
        vocab2 = self.VOCABULARIES.get(lang2, self.VOCABULARIES['english'])
        
        # Matrix language sentence with embedded phrase
        matrix_words = random.choices(vocab1['common'] + vocab1['everyday'], k=random.randint(4, 8))
        embedded_words = random.choices(vocab2['everyday'] + vocab2['social'], k=random.randint(2, 4))
        
        # Insert embedded phrase
        insert_pos = random.randint(1, len(matrix_words) - 1)
        words = matrix_words[:insert_pos] + embedded_words + matrix_words[insert_pos:]
        
        labels = ([lang1] * insert_pos + 
                 [lang2] * len(embedded_words) + 
                 [lang1] * (len(matrix_words) - insert_pos))
        
        switch_points = [insert_pos, insert_pos + len(embedded_words)]
        
        text = ' '.join(words)
        return text, labels, switch_points
    
    def _generate_edge_cases(self) -> List[SyntheticSample]:
        """Generate edge case samples for testing robustness."""
        edge_cases = []
        
        # Empty and very short texts
        edge_cases.extend([
            SyntheticSample(
                text="",
                languages=[],
                switch_points=[],
                ground_truth_labels=[],
                confidence_expected=0.0,
                difficulty_level="edge_case",
                domain="edge_case",
                pattern_type="empty",
                metadata={'is_code_mixed': False, 'edge_case_type': 'empty'}
            ),
            SyntheticSample(
                text="hi",
                languages=['english'],
                switch_points=[],
                ground_truth_labels=['english'],
                confidence_expected=0.6,
                difficulty_level="edge_case",
                domain="edge_case",
                pattern_type="very_short",
                metadata={'is_code_mixed': False, 'edge_case_type': 'very_short'}
            )
        ])
        
        # Numbers and symbols
        edge_cases.append(
            SyntheticSample(
                text="123 456 789",
                languages=[],
                switch_points=[],
                ground_truth_labels=['numeric', 'numeric', 'numeric'],
                confidence_expected=0.1,
                difficulty_level="edge_case",
                domain="edge_case",
                pattern_type="numeric",
                metadata={'is_code_mixed': False, 'edge_case_type': 'numeric'}
            )
        )
        
        # Mixed scripts (if romanization enabled)
        if self.config.include_romanization:
            edge_cases.append(
                SyntheticSample(
                    text="namaste नमस्ते hello",
                    languages=['hindi', 'english'],
                    switch_points=[1, 2],
                    ground_truth_labels=['hindi', 'hindi', 'english'],
                    confidence_expected=0.4,
                    difficulty_level="edge_case",
                    domain="edge_case",
                    pattern_type="mixed_script",
                    metadata={'is_code_mixed': True, 'edge_case_type': 'mixed_script'}
                )
            )
        
        print(f"✅ Generated {len(edge_cases)} edge case samples")
        return edge_cases
    
    def _print_statistics(self):
        """Print generation statistics."""
        print("\n📊 Generation Statistics:")
        print("-" * 30)
        
        total_samples = len(self.samples)
        code_mixed = sum(1 for s in self.samples if s.metadata.get('is_code_mixed', False))
        monolingual = total_samples - code_mixed
        
        print(f"Total samples: {total_samples}")
        print(f"Code-mixed: {code_mixed} ({code_mixed/total_samples:.1%})")
        print(f"Monolingual: {monolingual} ({monolingual/total_samples:.1%})")
        
        # Pattern distribution
        pattern_counts = defaultdict(int)
        for sample in self.samples:
            pattern_counts[sample.pattern_type] += 1
        
        print(f"\nPattern distribution:")
        for pattern, count in pattern_counts.items():
            print(f"  {pattern}: {count} ({count/total_samples:.1%})")
        
        # Language distribution
        lang_counts = defaultdict(int)
        for sample in self.samples:
            for lang in sample.languages:
                lang_counts[lang] += 1
        
        print(f"\nLanguage distribution:")
        for lang, count in lang_counts.items():
            print(f"  {lang}: {count}")
    
    def save_dataset(self, output_path: str, format: str = 'csv') -> bool:
        """Save generated dataset to file.
        
        Args:
            output_path: Path to save dataset
            format: Output format ('csv', 'json', 'jsonl')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert samples to serializable format
            data = [sample.to_dict() for sample in self.samples]
            
            if format == 'csv':
                df = pd.DataFrame(data)
                df.to_csv(output_path, index=False)
            elif format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'jsonl':
                with open(output_path, 'w', encoding='utf-8') as f:
                    for sample in data:
                        f.write(json.dumps(sample, ensure_ascii=False) + '\n')
            else:
                print(f"❌ Unsupported format: {format}")
                return False
            
            print(f"✅ Dataset saved to {output_path} ({format} format)")
            return True
            
        except Exception as e:
            print(f"❌ Error saving dataset: {e}")
            return False
    
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """Get metrics for evaluating the generated dataset quality.
        
        Returns:
            Dictionary of quality metrics
        """
        if not self.samples:
            return {}
        
        # Basic statistics
        total_samples = len(self.samples)
        code_mixed_count = sum(1 for s in self.samples if s.metadata.get('is_code_mixed', False))
        
        # Switch point statistics
        switch_counts = [len(s.switch_points) for s in self.samples if s.switch_points]
        avg_switches = np.mean(switch_counts) if switch_counts else 0
        
        # Token count statistics  
        token_counts = [s.metadata.get('token_count', 0) for s in self.samples]
        avg_tokens = np.mean(token_counts)
        
        # Confidence distribution
        confidences = [s.confidence_expected for s in self.samples]
        
        # Pattern diversity
        patterns = set(s.pattern_type for s in self.samples)
        
        # Language coverage
        all_languages = set()
        for sample in self.samples:
            all_languages.update(sample.languages)
        
        return {
            'total_samples': total_samples,
            'code_mixed_ratio': code_mixed_count / total_samples,
            'avg_switch_points': avg_switches,
            'avg_token_count': avg_tokens,
            'confidence_range': (min(confidences), max(confidences)),
            'avg_confidence': np.mean(confidences),
            'pattern_diversity': len(patterns),
            'patterns': list(patterns),
            'language_coverage': len(all_languages),
            'languages': list(all_languages),
            'difficulty_distribution': {
                level: sum(1 for s in self.samples if s.difficulty_level == level)
                for level in self.config.difficulty_levels
            },
            'domain_distribution': {
                domain: sum(1 for s in self.samples if s.domain == domain)
                for domain in self.config.domains
            }
        }


def main():
    """Example usage of synthetic data generator."""
    # Configuration
    config = SyntheticDataConfig(
        languages=['english', 'spanish', 'hindi'],
        sample_count=500,
        code_mixing_ratio=0.6,
        switch_patterns=['intrasentential', 'intersentential', 'tag_switching', 'borrowing'],
        domains=['casual_conversation', 'social_media', 'work', 'education'],
        difficulty_levels=['easy', 'medium', 'hard'],
        include_edge_cases=True,
        include_romanization=True,
        include_social_media=True,
        seed=42
    )
    
    # Generate dataset
    generator = SyntheticDataGenerator(config)
    samples = generator.generate_dataset()
    
    # Save dataset
    generator.save_dataset('synthetic_multilingual_dataset.csv', 'csv')
    generator.save_dataset('synthetic_multilingual_dataset.json', 'json')
    
    # Print quality metrics
    metrics = generator.get_evaluation_metrics()
    print(f"\n📊 Dataset Quality Metrics:")
    print(f"=" * 40)
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()