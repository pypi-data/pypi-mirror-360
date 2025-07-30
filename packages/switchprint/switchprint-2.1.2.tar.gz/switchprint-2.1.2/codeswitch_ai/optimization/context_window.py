#!/usr/bin/env python3
"""
Context Window Optimization for Code-Switching Detection

Optimizes word analysis window sizes for different text types to improve 
switch detection accuracy and overall performance.

Key Features:
1. Adaptive context window sizing based on text characteristics
2. Dynamic context boundary detection
3. Context-aware language prediction
4. Switch point refinement using context
5. Performance vs accuracy optimization
"""

import re
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

from ..detection.general_cs_detector import WordAnalysis, GeneralCSResult, GeneralCodeSwitchingDetector


class TextType(Enum):
    """Text type classification for context optimization."""
    SHORT_SOCIAL = "short_social"      # Social media posts, tweets (< 5 words)
    MEDIUM_CHAT = "medium_chat"        # Chat messages, SMS (5-15 words)
    LONG_DOCUMENT = "long_document"    # Documents, articles (> 15 words)
    CONVERSATION = "conversation"      # Dialog, conversation turns
    MIXED_CONTENT = "mixed_content"    # Mixed content types


@dataclass
class ContextConfig:
    """Configuration for context window optimization."""
    window_size: int                    # Base context window size
    overlap_size: int                   # Overlap between windows
    min_confidence_threshold: float     # Minimum confidence for context decisions
    context_boost_factor: float         # Boost factor for contextual predictions
    adaptive_sizing: bool              # Enable adaptive window sizing
    max_window_size: int               # Maximum window size for long texts
    min_window_size: int               # Minimum window size for short texts


@dataclass
class ContextualWordAnalysis:
    """Enhanced word analysis with context information."""
    word_analysis: WordAnalysis
    context_window: List[str]          # Surrounding words
    context_languages: List[str]       # Languages detected in context
    context_confidence: float          # Confidence based on context
    contextual_prediction: str         # Language prediction with context
    contextual_confidence: float       # Confidence with context boost
    context_reasoning: str             # Reason for contextual decision
    window_position: int               # Position within context window


@dataclass
class ContextOptimizationResult:
    """Result of context window optimization."""
    original_result: GeneralCSResult
    optimized_result: GeneralCSResult
    context_analyses: List[ContextualWordAnalysis]
    text_type: TextType
    window_config: ContextConfig
    performance_metrics: Dict[str, Any]
    improvement_score: float


class ContextWindowOptimizer:
    """Optimizes context windows for improved code-switching detection."""
    
    def __init__(self, detector: Optional[GeneralCodeSwitchingDetector] = None):
        """Initialize context window optimizer."""
        self.detector = detector or GeneralCodeSwitchingDetector()
        
        # Context configurations for different text types
        self.context_configs = {
            TextType.SHORT_SOCIAL: ContextConfig(
                window_size=3,
                overlap_size=1,
                min_confidence_threshold=0.3,
                context_boost_factor=0.2,
                adaptive_sizing=True,
                max_window_size=5,
                min_window_size=2
            ),
            TextType.MEDIUM_CHAT: ContextConfig(
                window_size=5,
                overlap_size=2,
                min_confidence_threshold=0.4,
                context_boost_factor=0.3,
                adaptive_sizing=True,
                max_window_size=7,
                min_window_size=3
            ),
            TextType.LONG_DOCUMENT: ContextConfig(
                window_size=7,
                overlap_size=3,
                min_confidence_threshold=0.5,
                context_boost_factor=0.25,
                adaptive_sizing=True,
                max_window_size=10,
                min_window_size=5
            ),
            TextType.CONVERSATION: ContextConfig(
                window_size=4,
                overlap_size=2,
                min_confidence_threshold=0.35,
                context_boost_factor=0.35,
                adaptive_sizing=True,
                max_window_size=6,
                min_window_size=3
            ),
            TextType.MIXED_CONTENT: ContextConfig(
                window_size=5,
                overlap_size=2,
                min_confidence_threshold=0.4,
                context_boost_factor=0.3,
                adaptive_sizing=True,
                max_window_size=8,
                min_window_size=3
            )
        }
        
        # Performance tracking
        self.optimization_stats = {
            'total_optimizations': 0,
            'accuracy_improvements': 0,
            'switch_point_improvements': 0,
            'avg_processing_time': 0.0
        }
        
        print("🎯 Context Window Optimizer initialized")
    
    def optimize_detection(self, text: str, 
                          user_languages: Optional[List[str]] = None) -> ContextOptimizationResult:
        """Optimize detection using context window analysis."""
        
        start_time = time.time()
        
        # Classify text type
        text_type = self._classify_text_type(text)
        config = self.context_configs[text_type]
        
        # Get original detection result
        original_result = self.detector.detect_language(text, user_languages)
        
        # Perform context-aware analysis
        context_analyses = self._analyze_with_context(text, config)
        
        # Create optimized result
        optimized_result = self._create_optimized_result(
            original_result, context_analyses, text, config
        )
        
        # Calculate performance metrics
        processing_time = time.time() - start_time
        performance_metrics = self._calculate_performance_metrics(
            original_result, optimized_result, processing_time
        )
        
        # Calculate improvement score
        improvement_score = self._calculate_improvement_score(
            original_result, optimized_result
        )
        
        # Update stats
        self.optimization_stats['total_optimizations'] += 1
        if improvement_score > 0:
            self.optimization_stats['accuracy_improvements'] += 1
        
        self.optimization_stats['avg_processing_time'] = (
            (self.optimization_stats['avg_processing_time'] * 
             (self.optimization_stats['total_optimizations'] - 1) + processing_time) /
            self.optimization_stats['total_optimizations']
        )
        
        return ContextOptimizationResult(
            original_result=original_result,
            optimized_result=optimized_result,
            context_analyses=context_analyses,
            text_type=text_type,
            window_config=config,
            performance_metrics=performance_metrics,
            improvement_score=improvement_score
        )
    
    def _classify_text_type(self, text: str) -> TextType:
        """Classify text type for context optimization."""
        
        words = text.split()
        word_count = len(words)
        
        # Analyze text characteristics
        has_social_markers = bool(re.search(r'[#@]|\b(lol|omg|wtf|tbh|imo)\b', text.lower()))
        has_punctuation_patterns = bool(re.search(r'[!]{2,}|[?]{2,}|\.{3,}', text))
        has_conversational_markers = bool(re.search(r'\b(well|so|but|and|um|uh)\b', text.lower()))
        sentence_count = len(re.split(r'[.!?]+', text.strip()))
        
        # Classification logic
        if word_count <= 5:
            if has_social_markers or has_punctuation_patterns:
                return TextType.SHORT_SOCIAL
            else:
                return TextType.MEDIUM_CHAT
        elif word_count <= 15:
            if has_conversational_markers:
                return TextType.CONVERSATION
            else:
                return TextType.MEDIUM_CHAT
        else:
            if sentence_count > 3:
                return TextType.LONG_DOCUMENT
            else:
                return TextType.MIXED_CONTENT
    
    def _analyze_with_context(self, text: str, config: ContextConfig) -> List[ContextualWordAnalysis]:
        """Analyze text with context windows."""
        
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return []
        
        context_analyses = []
        
        # Calculate adaptive window size
        if config.adaptive_sizing:
            window_size = self._calculate_adaptive_window_size(words, config)
        else:
            window_size = config.window_size
        
        # Analyze each word with context
        for i, word in enumerate(words):
            if len(word) < 2:  # Skip very short words
                continue
            
            # Extract context window
            context_start = max(0, i - window_size // 2)
            context_end = min(len(words), i + window_size // 2 + 1)
            context_window = words[context_start:context_end]
            
            # Get original word analysis
            word_analysis = self._get_word_analysis(word, i)
            
            # Analyze context
            context_languages = self._analyze_context_languages(context_window, word)
            context_confidence = self._calculate_context_confidence(
                context_languages, word_analysis
            )
            
            # Make contextual prediction
            contextual_prediction, contextual_confidence, reasoning = self._make_contextual_prediction(
                word_analysis, context_languages, context_confidence, config
            )
            
            context_analysis = ContextualWordAnalysis(
                word_analysis=word_analysis,
                context_window=context_window,
                context_languages=context_languages,
                context_confidence=context_confidence,
                contextual_prediction=contextual_prediction,
                contextual_confidence=contextual_confidence,
                context_reasoning=reasoning,
                window_position=i - context_start
            )
            
            context_analyses.append(context_analysis)
        
        return context_analyses
    
    def _calculate_adaptive_window_size(self, words: List[str], config: ContextConfig) -> int:
        """Calculate adaptive window size based on text characteristics."""
        
        word_count = len(words)
        
        # Base calculation on text length
        if word_count <= 5:
            base_size = config.min_window_size
        elif word_count <= 15:
            base_size = config.window_size
        else:
            base_size = min(config.max_window_size, config.window_size + word_count // 10)
        
        # Adjust for text complexity
        complex_words = sum(1 for word in words if len(word) > 6)
        complexity_factor = complex_words / len(words) if words else 0
        
        if complexity_factor > 0.3:  # High complexity
            base_size = min(config.max_window_size, base_size + 1)
        elif complexity_factor < 0.1:  # Low complexity
            base_size = max(config.min_window_size, base_size - 1)
        
        return base_size
    
    def _get_word_analysis(self, word: str, position: int) -> WordAnalysis:
        """Get word analysis using the detector's method."""
        
        # Create temporary single-word analysis
        try:
            ft_result = self.detector.fasttext.detect_language(word)
            ft_lang = ft_result.detected_languages[0] if ft_result.detected_languages else 'unknown'
            ft_conf = ft_result.confidence
            
            # Simplified analysis for context optimization
            return WordAnalysis(
                word=word,
                position=position,
                fasttext_prediction=ft_lang,
                fasttext_confidence=ft_conf,
                transformer_prediction=None,
                transformer_confidence=None,
                final_prediction=ft_lang,
                final_confidence=ft_conf,
                reasoning="context_analysis"
            )
        except Exception:
            return WordAnalysis(
                word=word,
                position=position,
                fasttext_prediction='unknown',
                fasttext_confidence=0.0,
                transformer_prediction=None,
                transformer_confidence=None,
                final_prediction='unknown',
                final_confidence=0.0,
                reasoning="context_analysis_failed"
            )
    
    def _analyze_context_languages(self, context_window: List[str], target_word: str) -> List[str]:
        """Analyze languages in the context window."""
        
        context_languages = []
        
        for word in context_window:
            if word != target_word and len(word) >= 2:
                try:
                    result = self.detector.fasttext.detect_language(word)
                    if result.detected_languages and result.confidence > 0.3:
                        lang = result.detected_languages[0]
                        if lang not in context_languages:
                            context_languages.append(lang)
                except Exception:
                    continue
        
        return context_languages
    
    def _calculate_context_confidence(self, context_languages: List[str], 
                                    word_analysis: WordAnalysis) -> float:
        """Calculate confidence based on context consistency."""
        
        if not context_languages:
            return 0.0
        
        # Check if word's prediction is consistent with context
        word_lang = word_analysis.final_prediction
        
        if word_lang in context_languages:
            # Consistent with context
            consistency_score = 0.8
        elif word_lang == 'unknown':
            # Unknown word, moderate confidence from context
            consistency_score = 0.5
        else:
            # Inconsistent with context (potential switch point)
            consistency_score = 0.3
        
        # Factor in original confidence
        context_confidence = (
            consistency_score * 0.7 + word_analysis.final_confidence * 0.3
        )
        
        return context_confidence
    
    def _make_contextual_prediction(self, word_analysis: WordAnalysis,
                                  context_languages: List[str],
                                  context_confidence: float,
                                  config: ContextConfig) -> Tuple[str, float, str]:
        """Make contextual language prediction."""
        
        original_lang = word_analysis.final_prediction
        original_conf = word_analysis.final_confidence
        
        # If original prediction is confident and consistent, keep it
        if original_conf >= config.min_confidence_threshold and context_confidence >= 0.6:
            boosted_conf = min(1.0, original_conf + config.context_boost_factor)
            return original_lang, boosted_conf, "context_consistent_boost"
        
        # If original prediction is weak but context is strong
        elif original_conf < config.min_confidence_threshold and context_languages:
            # Use most common context language
            context_lang = context_languages[0]  # Simplified - could be improved
            context_based_conf = min(0.8, context_confidence + config.context_boost_factor)
            return context_lang, context_based_conf, "context_override"
        
        # If context suggests a switch point
        elif (context_languages and 
              original_lang not in context_languages and 
              original_conf >= config.min_confidence_threshold):
            # Maintain original but flag as potential switch
            return original_lang, original_conf, "potential_switch_point"
        
        # Default case
        else:
            return original_lang, original_conf, "no_context_change"
    
    def _create_optimized_result(self, original_result: GeneralCSResult,
                               context_analyses: List[ContextualWordAnalysis],
                               text: str, config: ContextConfig) -> GeneralCSResult:
        """Create optimized detection result using context analysis."""
        
        # Extract enhanced word analyses
        enhanced_word_analyses = []
        for ctx_analysis in context_analyses:
            # Update word analysis with contextual information
            enhanced_analysis = WordAnalysis(
                word=ctx_analysis.word_analysis.word,
                position=ctx_analysis.word_analysis.position,
                fasttext_prediction=ctx_analysis.word_analysis.fasttext_prediction,
                fasttext_confidence=ctx_analysis.word_analysis.fasttext_confidence,
                transformer_prediction=ctx_analysis.word_analysis.transformer_prediction,
                transformer_confidence=ctx_analysis.word_analysis.transformer_confidence,
                final_prediction=ctx_analysis.contextual_prediction,
                final_confidence=ctx_analysis.contextual_confidence,
                reasoning=f"context_optimized_{ctx_analysis.context_reasoning}"
            )
            enhanced_word_analyses.append(enhanced_analysis)
        
        # Recalculate language probabilities based on enhanced analysis
        enhanced_probabilities = self._recalculate_probabilities(enhanced_word_analyses)
        
        # Determine languages using enhanced probabilities
        threshold = self.detector.threshold_config.get_inclusion_threshold()
        detected_languages = [
            lang for lang, prob in enhanced_probabilities.items() 
            if prob >= threshold
        ]
        
        # Sort by probability
        detected_languages.sort(key=lambda l: enhanced_probabilities[l], reverse=True)
        
        # Ensure at least one language
        if not detected_languages and enhanced_probabilities:
            best_lang = max(enhanced_probabilities.keys(), key=lambda l: enhanced_probabilities[l])
            if enhanced_probabilities[best_lang] >= 0.1:
                detected_languages = [best_lang]
        
        # Recalculate switch points with context
        enhanced_switch_points = self._find_enhanced_switch_points(enhanced_word_analyses)
        
        # Calculate enhanced confidence
        overall_confidence = (
            max(enhanced_probabilities[lang] for lang in detected_languages)
            if detected_languages else 0.0
        )
        
        # Determine if code-mixed
        is_code_mixed = len(detected_languages) > 1 and len(enhanced_switch_points) > 0
        
        return GeneralCSResult(
            detected_languages=detected_languages,
            confidence=overall_confidence,
            probabilities=enhanced_probabilities,
            word_analyses=enhanced_word_analyses,
            switch_points=enhanced_switch_points,
            method="context_optimized",
            is_code_mixed=is_code_mixed,
            quality_metrics=self._calculate_enhanced_quality_metrics(
                enhanced_word_analyses, text, config
            ),
            debug_info={
                'context_window_size': config.window_size,
                'text_type': config.__class__.__name__,
                'context_boost_applied': True
            }
        )
    
    def _recalculate_probabilities(self, word_analyses: List[WordAnalysis]) -> Dict[str, float]:
        """Recalculate language probabilities from enhanced word analyses."""
        
        language_scores = {}
        
        for analysis in word_analyses:
            lang = analysis.final_prediction
            conf = analysis.final_confidence
            
            if lang != 'unknown':
                if lang in language_scores:
                    language_scores[lang] += conf
                else:
                    language_scores[lang] = conf
        
        # Normalize probabilities
        if language_scores:
            total_score = sum(language_scores.values())
            normalized_probs = {
                lang: score / total_score 
                for lang, score in language_scores.items()
            }
            return normalized_probs
        
        return {}
    
    def _find_enhanced_switch_points(self, word_analyses: List[WordAnalysis]) -> List[Dict[str, Any]]:
        """Find switch points using enhanced context analysis."""
        
        switch_points = []
        prev_lang = None
        
        for i, analysis in enumerate(word_analyses):
            current_lang = analysis.final_prediction
            
            # Enhanced switch detection with context reasoning
            is_context_switch = "potential_switch_point" in analysis.reasoning
            is_confident_change = (
                prev_lang and 
                current_lang != prev_lang and 
                current_lang != 'unknown' and 
                prev_lang != 'unknown' and
                analysis.final_confidence >= 0.4
            )
            
            if is_confident_change or is_context_switch:
                switch_point = {
                    "position": i,
                    "from_language": prev_lang,
                    "to_language": current_lang,
                    "word": analysis.word,
                    "confidence": analysis.final_confidence,
                    "context_enhanced": True,
                    "switch_type": "context_detected" if is_context_switch else "confidence_based",
                    "context": {
                        "previous_word": word_analyses[i-1].word if i > 0 else None,
                        "current_word": analysis.word,
                        "reasoning": analysis.reasoning
                    }
                }
                switch_points.append(switch_point)
            
            if current_lang != 'unknown':
                prev_lang = current_lang
        
        return switch_points
    
    def _calculate_enhanced_quality_metrics(self, word_analyses: List[WordAnalysis],
                                          text: str, config: ContextConfig) -> Dict[str, Any]:
        """Calculate enhanced quality metrics."""
        
        context_boost_count = sum(
            1 for analysis in word_analyses 
            if "context_consistent_boost" in analysis.reasoning
        )
        
        context_override_count = sum(
            1 for analysis in word_analyses 
            if "context_override" in analysis.reasoning
        )
        
        switch_point_count = sum(
            1 for analysis in word_analyses 
            if "potential_switch_point" in analysis.reasoning
        )
        
        return {
            "context_window_size": config.window_size,
            "context_boosts_applied": context_boost_count,
            "context_overrides_applied": context_override_count,
            "potential_switches_detected": switch_point_count,
            "context_coverage": len(word_analyses) / len(text.split()) if text.split() else 0,
            "avg_contextual_confidence": np.mean([w.final_confidence for w in word_analyses]) if word_analyses else 0
        }
    
    def _calculate_performance_metrics(self, original: GeneralCSResult,
                                     optimized: GeneralCSResult,
                                     processing_time: float) -> Dict[str, Any]:
        """Calculate performance improvement metrics."""
        
        return {
            "processing_time_ms": processing_time * 1000,
            "confidence_change": optimized.confidence - original.confidence,
            "language_count_change": len(optimized.detected_languages) - len(original.detected_languages),
            "switch_points_change": len(optimized.switch_points) - len(original.switch_points),
            "accuracy_improvement": self._estimate_accuracy_improvement(original, optimized),
            "word_analysis_enhancement": len(optimized.word_analyses) / max(1, len(original.word_analyses))
        }
    
    def _estimate_accuracy_improvement(self, original: GeneralCSResult, 
                                     optimized: GeneralCSResult) -> float:
        """Estimate accuracy improvement (simplified heuristic)."""
        
        # Simple heuristic based on confidence and consistency
        confidence_improvement = optimized.confidence - original.confidence
        
        # Check switch point quality
        switch_quality_improvement = 0.0
        if len(optimized.switch_points) > 0:
            avg_switch_conf = np.mean([
                sp.get('confidence', 0) for sp in optimized.switch_points
            ])
            if len(original.switch_points) > 0:
                orig_avg_switch_conf = np.mean([
                    sp.get('confidence', 0) for sp in original.switch_points
                ])
                switch_quality_improvement = avg_switch_conf - orig_avg_switch_conf
            else:
                switch_quality_improvement = avg_switch_conf * 0.5
        
        return confidence_improvement * 0.7 + switch_quality_improvement * 0.3
    
    def _calculate_improvement_score(self, original: GeneralCSResult, 
                                   optimized: GeneralCSResult) -> float:
        """Calculate overall improvement score."""
        
        # Weighted combination of different improvement metrics
        confidence_weight = 0.4
        switch_quality_weight = 0.3
        consistency_weight = 0.3
        
        confidence_improvement = max(0, optimized.confidence - original.confidence)
        
        switch_improvement = 0.0
        if len(optimized.switch_points) > len(original.switch_points):
            switch_improvement = 0.1 * (len(optimized.switch_points) - len(original.switch_points))
        
        consistency_improvement = 0.0
        if optimized.quality_metrics and original.quality_metrics:
            opt_coverage = optimized.quality_metrics.get('context_coverage', 0)
            orig_coverage = original.quality_metrics.get('word_analysis_coverage', 0)
            consistency_improvement = max(0, opt_coverage - orig_coverage)
        
        improvement_score = (
            confidence_improvement * confidence_weight +
            switch_improvement * switch_quality_weight +
            consistency_improvement * consistency_weight
        )
        
        return improvement_score
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization performance statistics."""
        
        stats = self.optimization_stats.copy()
        
        if stats['total_optimizations'] > 0:
            stats['improvement_rate'] = stats['accuracy_improvements'] / stats['total_optimizations']
        else:
            stats['improvement_rate'] = 0.0
        
        return stats
    
    def benchmark_window_sizes(self, test_texts: List[str], 
                              window_sizes: List[int] = [3, 5, 7, 10]) -> Dict[str, Any]:
        """Benchmark different window sizes on test texts."""
        
        print(f"🏁 Benchmarking context window sizes: {window_sizes}")
        
        results = {}
        
        for window_size in window_sizes:
            print(f"  Testing window size: {window_size}")
            
            # Temporarily modify configs
            original_configs = {}
            for text_type in TextType:
                original_configs[text_type] = self.context_configs[text_type].window_size
                self.context_configs[text_type].window_size = window_size
            
            # Test on all texts
            total_improvement = 0.0
            processing_times = []
            
            for text in test_texts:
                start_time = time.time()
                result = self.optimize_detection(text)
                processing_time = time.time() - start_time
                
                total_improvement += result.improvement_score
                processing_times.append(processing_time)
            
            # Calculate metrics
            avg_improvement = total_improvement / len(test_texts)
            avg_processing_time = np.mean(processing_times)
            
            results[f"window_{window_size}"] = {
                'avg_improvement_score': avg_improvement,
                'avg_processing_time_ms': avg_processing_time * 1000,
                'total_improvement': total_improvement,
                'efficiency_score': avg_improvement / max(0.001, avg_processing_time)
            }
            
            # Restore original configs
            for text_type in TextType:
                self.context_configs[text_type].window_size = original_configs[text_type]
        
        # Find best configuration
        best_config = max(results.items(), key=lambda x: x[1]['efficiency_score'])
        
        print(f"🏆 Best window size: {best_config[0]} (efficiency: {best_config[1]['efficiency_score']:.3f})")
        
        return {
            'results': results,
            'best_config': best_config[0],
            'best_metrics': best_config[1]
        }


def demo_context_optimization():
    """Demonstrate context window optimization."""
    
    print("🎯 CONTEXT WINDOW OPTIMIZATION DEMO")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = ContextWindowOptimizer()
    
    # Test cases with different text types
    test_cases = [
        # Short social media
        ("OMG this is amazing!", "Short social media post"),
        ("LOL yes totally agree", "Chat response"),
        
        # Medium chat
        ("I'm going to the mercado later, want to come with me?", "Code-switching chat"),
        ("Hello, ¿cómo estás? I hope you're doing bien today", "Mixed language greeting"),
        
        # Long document
        ("This is a longer document that discusses the importance of multilingual communication in today's globalized world.", "Long monolingual text"),
        ("In today's business environment, it's common to switch between English and español during meetings, especially when discussing mercado strategies.", "Long code-switching text"),
        
        # Conversation
        ("Well, I think we should go but first let me ask mama", "Conversational with code-switch"),
        ("So what do you think about the new película that just came out?", "Question with code-switch")
    ]
    
    print(f"📝 Testing {len(test_cases)} diverse text samples")
    print()
    
    improvements = []
    
    for i, (text, description) in enumerate(test_cases, 1):
        print(f"{i}. {description}")
        print(f"   Text: \"{text}\"")
        
        # Run optimization
        result = optimizer.optimize_detection(text)
        
        print(f"   Text Type: {result.text_type.value}")
        print(f"   Window Size: {result.window_config.window_size}")
        print(f"   Original: {result.original_result.detected_languages} (conf: {result.original_result.confidence:.3f})")
        print(f"   Optimized: {result.optimized_result.detected_languages} (conf: {result.optimized_result.confidence:.3f})")
        print(f"   Improvement: {result.improvement_score:+.3f}")
        print(f"   Switch Points: {len(result.original_result.switch_points)} → {len(result.optimized_result.switch_points)}")
        print()
        
        improvements.append(result.improvement_score)
    
    # Summary statistics
    print("📊 OPTIMIZATION SUMMARY")
    print("=" * 40)
    print(f"Average improvement: {np.mean(improvements):+.3f}")
    print(f"Positive improvements: {sum(1 for imp in improvements if imp > 0)}/{len(improvements)}")
    print(f"Max improvement: {max(improvements):+.3f}")
    
    # Performance stats
    stats = optimizer.get_optimization_stats()
    print(f"Total optimizations: {stats['total_optimizations']}")
    print(f"Average processing time: {stats['avg_processing_time']*1000:.1f}ms")
    
    # Benchmark window sizes
    print("\n🏁 WINDOW SIZE BENCHMARKING")
    print("=" * 40)
    
    benchmark_texts = [case[0] for case in test_cases]
    benchmark_results = optimizer.benchmark_window_sizes(benchmark_texts)
    
    print("Window size performance:")
    for config, metrics in benchmark_results['results'].items():
        print(f"  {config}: improvement={metrics['avg_improvement_score']:+.3f}, "
              f"time={metrics['avg_processing_time_ms']:.1f}ms, "
              f"efficiency={metrics['efficiency_score']:.3f}")
    
    print(f"\n🏆 Best configuration: {benchmark_results['best_config']}")
    
    return optimizer, test_cases, benchmark_results


if __name__ == "__main__":
    demo_context_optimization()