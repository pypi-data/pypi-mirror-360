#!/usr/bin/env python3
"""
Context-Enhanced General Code-Switching Detector

Extends the GeneralCSDetector with context window optimization for improved
switch detection accuracy and overall performance.
"""

from typing import List, Optional, Dict, Any
import time

from .general_cs_detector import GeneralCodeSwitchingDetector, GeneralCSResult
from ..optimization.context_window import ContextWindowOptimizer, ContextOptimizationResult


class ContextEnhancedCSDetector(GeneralCodeSwitchingDetector):
    """Enhanced detector with context window optimization."""
    
    def __init__(self, 
                 performance_mode: str = "balanced",
                 detector_mode: str = "code_switching", 
                 enable_context_optimization: bool = True,
                 context_optimization_threshold: float = 0.1,
                 **kwargs):
        """Initialize context-enhanced detector.
        
        Args:
            performance_mode: Performance mode (fast/balanced/accurate)
            detector_mode: Detector mode (code_switching/monolingual/multilingual)
            enable_context_optimization: Whether to enable context optimization
            context_optimization_threshold: Minimum improvement threshold for using optimization
            **kwargs: Additional arguments passed to parent class
        """
        
        super().__init__(performance_mode=performance_mode, detector_mode=detector_mode, **kwargs)
        
        self.enable_context_optimization = enable_context_optimization
        self.context_optimization_threshold = context_optimization_threshold
        
        # Initialize context optimizer
        if self.enable_context_optimization:
            self.context_optimizer = ContextWindowOptimizer(detector=self)
        else:
            self.context_optimizer = None
        
        # Performance tracking
        self.context_stats = {
            'total_detections': 0,
            'context_optimizations_used': 0,
            'avg_improvement': 0.0,
            'avg_optimization_time': 0.0
        }
        
        print(f"🎯 Context-Enhanced CS Detector initialized")
        print(f"   Context optimization: {enable_context_optimization}")
        print(f"   Improvement threshold: {context_optimization_threshold}")
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> GeneralCSResult:
        """Detect language with optional context optimization."""
        
        start_time = time.time()
        self.context_stats['total_detections'] += 1
        
        # Get base detection result
        base_result = super().detect_language(text, user_languages)
        
        # Apply context optimization if enabled and beneficial
        if (self.enable_context_optimization and 
            self.context_optimizer and
            self._should_optimize(text, base_result)):
            
            try:
                optimization_start = time.time()
                
                # Run context optimization
                optimization_result = self.context_optimizer.optimize_detection(text, user_languages)
                
                optimization_time = time.time() - optimization_start
                
                # Use optimized result if improvement is significant
                if optimization_result.improvement_score >= self.context_optimization_threshold:
                    self.context_stats['context_optimizations_used'] += 1
                    
                    # Update stats
                    self._update_optimization_stats(optimization_result.improvement_score, optimization_time)
                    
                    # Enhance result with optimization metadata
                    optimized_result = optimization_result.optimized_result
                    optimized_result.debug_info.update({
                        'context_optimization_applied': True,
                        'improvement_score': optimization_result.improvement_score,
                        'optimization_time_ms': optimization_time * 1000,
                        'text_type': optimization_result.text_type.value,
                        'window_size': optimization_result.window_config.window_size
                    })
                    
                    return optimized_result
                else:
                    # Optimization didn't meet threshold, use base result
                    base_result.debug_info['context_optimization_attempted'] = True
                    base_result.debug_info['optimization_below_threshold'] = True
                    return base_result
                    
            except Exception as e:
                # Fallback to base result if optimization fails
                base_result.debug_info['context_optimization_failed'] = str(e)
                return base_result
        
        else:
            # Context optimization disabled or not needed
            base_result.debug_info['context_optimization_skipped'] = True
            return base_result
    
    def _should_optimize(self, text: str, base_result: GeneralCSResult) -> bool:
        """Determine if context optimization should be applied."""
        
        # Skip optimization for very short texts (insufficient context)
        words = text.split()
        if len(words) < 3:
            return False
        
        # Skip if base result is already highly confident and monolingual
        if (base_result.confidence > 0.8 and 
            len(base_result.detected_languages) == 1 and 
            not base_result.switch_points):
            return False
        
        # Optimize for potential code-switching cases
        if (len(base_result.detected_languages) > 1 or 
            base_result.switch_points or
            base_result.confidence < 0.6):
            return True
        
        # Optimize for medium confidence cases that might benefit
        if 0.4 <= base_result.confidence <= 0.7:
            return True
        
        return False
    
    def _update_optimization_stats(self, improvement_score: float, optimization_time: float):
        """Update optimization performance statistics."""
        
        # Update average improvement
        current_optimizations = self.context_stats['context_optimizations_used']
        prev_avg_improvement = self.context_stats['avg_improvement']
        
        self.context_stats['avg_improvement'] = (
            (prev_avg_improvement * (current_optimizations - 1) + improvement_score) / 
            current_optimizations
        )
        
        # Update average optimization time
        prev_avg_time = self.context_stats['avg_optimization_time']
        self.context_stats['avg_optimization_time'] = (
            (prev_avg_time * (current_optimizations - 1) + optimization_time) / 
            current_optimizations
        )
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context optimization statistics."""
        
        stats = self.context_stats.copy()
        
        if stats['total_detections'] > 0:
            stats['optimization_rate'] = stats['context_optimizations_used'] / stats['total_detections']
        else:
            stats['optimization_rate'] = 0.0
        
        if self.context_optimizer:
            optimizer_stats = self.context_optimizer.get_optimization_stats()
            stats['optimizer_stats'] = optimizer_stats
        
        return stats
    
    def enable_context_optimization_for_mode(self, mode: str):
        """Enable context optimization for specific detector mode."""
        
        if mode == "code_switching":
            self.context_optimization_threshold = 0.05  # Lower threshold for CS detection
        elif mode == "monolingual":
            self.context_optimization_threshold = 0.2   # Higher threshold for monolingual
        elif mode == "multilingual":
            self.context_optimization_threshold = 0.1   # Balanced threshold
        
        print(f"🎯 Context optimization configured for {mode} mode (threshold: {self.context_optimization_threshold})")
    
    def benchmark_context_optimization(self, test_texts: List[str]) -> Dict[str, Any]:
        """Benchmark context optimization performance."""
        
        if not self.context_optimizer:
            return {"error": "Context optimization not enabled"}
        
        print(f"🏁 Benchmarking context optimization on {len(test_texts)} texts")
        
        base_results = []
        optimized_results = []
        improvements = []
        processing_times = []
        
        for text in test_texts:
            # Get base result (without optimization)
            temp_enabled = self.enable_context_optimization
            self.enable_context_optimization = False
            
            start_time = time.time()
            base_result = self.detect_language(text)
            base_time = time.time() - start_time
            
            # Get optimized result
            self.enable_context_optimization = temp_enabled
            
            start_time = time.time()
            optimized_result = self.detect_language(text)
            optimized_time = time.time() - start_time
            
            base_results.append(base_result)
            optimized_results.append(optimized_result)
            processing_times.append({
                'base_time': base_time,
                'optimized_time': optimized_time,
                'overhead': optimized_time - base_time
            })
            
            # Calculate improvement
            if optimized_result.debug_info.get('context_optimization_applied'):
                improvement = optimized_result.debug_info.get('improvement_score', 0)
            else:
                improvement = 0.0
            improvements.append(improvement)
        
        # Calculate statistics
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        optimization_used_count = sum(1 for imp in improvements if imp > 0)
        avg_base_time = sum(pt['base_time'] for pt in processing_times) / len(processing_times)
        avg_optimized_time = sum(pt['optimized_time'] for pt in processing_times) / len(processing_times)
        avg_overhead = avg_optimized_time - avg_base_time
        
        return {
            'test_count': len(test_texts),
            'optimization_used_count': optimization_used_count,
            'optimization_rate': optimization_used_count / len(test_texts),
            'avg_improvement_score': avg_improvement,
            'max_improvement': max(improvements) if improvements else 0,
            'avg_base_time_ms': avg_base_time * 1000,
            'avg_optimized_time_ms': avg_optimized_time * 1000,
            'avg_overhead_ms': avg_overhead * 1000,
            'overhead_percentage': (avg_overhead / avg_base_time * 100) if avg_base_time > 0 else 0,
            'improvements': improvements,
            'processing_times': processing_times
        }
    
    def configure_adaptive_optimization(self, text_samples: List[str]):
        """Configure optimization thresholds based on text samples."""
        
        if not self.context_optimizer:
            print("⚠️ Context optimization not enabled")
            return
        
        print(f"🔧 Configuring adaptive optimization using {len(text_samples)} samples")
        
        # Benchmark different thresholds
        thresholds = [0.05, 0.1, 0.15, 0.2, 0.25]
        best_threshold = self.context_optimization_threshold
        best_efficiency = 0.0
        
        for threshold in thresholds:
            self.context_optimization_threshold = threshold
            
            benchmark_result = self.benchmark_context_optimization(text_samples[:20])  # Use subset
            
            # Calculate efficiency (improvement / overhead)
            avg_improvement = benchmark_result['avg_improvement_score']
            avg_overhead = benchmark_result['avg_overhead_ms']
            
            efficiency = avg_improvement / max(1.0, avg_overhead / 100)  # Normalize overhead
            
            print(f"  Threshold {threshold}: improvement={avg_improvement:.3f}, "
                  f"overhead={avg_overhead:.1f}ms, efficiency={efficiency:.3f}")
            
            if efficiency > best_efficiency:
                best_efficiency = efficiency
                best_threshold = threshold
        
        self.context_optimization_threshold = best_threshold
        print(f"🎯 Optimal threshold selected: {best_threshold} (efficiency: {best_efficiency:.3f})")


def demo_context_enhanced_detector():
    """Demonstrate context-enhanced detection capabilities."""
    
    print("🎯 CONTEXT-ENHANCED DETECTOR DEMO")
    print("=" * 60)
    
    # Initialize detectors for comparison
    base_detector = GeneralCodeSwitchingDetector(performance_mode="balanced")
    enhanced_detector = ContextEnhancedCSDetector(
        performance_mode="balanced",
        enable_context_optimization=True,
        context_optimization_threshold=0.1
    )
    
    # Test cases
    test_cases = [
        "Hello, ¿cómo estás? I hope you're doing bien today",
        "I'm going to the mercado later to buy some groceries",
        "Yallah let's go, we're already late for the meeting",
        "This is a longer English sentence that should not need optimization",
        "Hola mundo, this is a simple greeting",
        "Je suis très tired from all this work today",
        "Main ghar ja raha hoon but I'll be back soon",
        "Buenos días everyone, I hope you had a great weekend"
    ]
    
    print(f"📝 Testing {len(test_cases)} diverse examples")
    print()
    
    improvements_count = 0
    total_improvement = 0.0
    
    for i, text in enumerate(test_cases, 1):
        print(f"{i}. \"{text}\"")
        
        # Base detection
        base_result = base_detector.detect_language(text)
        
        # Enhanced detection
        enhanced_result = enhanced_detector.detect_language(text)
        
        print(f"   Base: {base_result.detected_languages} (conf: {base_result.confidence:.3f})")
        print(f"   Enhanced: {enhanced_result.detected_languages} (conf: {enhanced_result.confidence:.3f})")
        
        # Check if optimization was applied
        if enhanced_result.debug_info.get('context_optimization_applied'):
            improvement = enhanced_result.debug_info.get('improvement_score', 0)
            window_size = enhanced_result.debug_info.get('window_size', 'N/A')
            text_type = enhanced_result.debug_info.get('text_type', 'N/A')
            
            print(f"   ✨ Optimization applied: +{improvement:.3f} (window: {window_size}, type: {text_type})")
            improvements_count += 1
            total_improvement += improvement
        else:
            reason = enhanced_result.debug_info.get('context_optimization_skipped', 
                    enhanced_result.debug_info.get('optimization_below_threshold', 'not applied'))
            print(f"   ➖ No optimization: {reason}")
        
        print(f"   Switch points: {len(base_result.switch_points)} → {len(enhanced_result.switch_points)}")
        print()
    
    # Summary
    print("📊 ENHANCEMENT SUMMARY")
    print("=" * 40)
    print(f"Optimizations applied: {improvements_count}/{len(test_cases)}")
    print(f"Average improvement: {total_improvement/max(1, improvements_count):.3f}")
    
    # Get comprehensive stats
    context_stats = enhanced_detector.get_context_stats()
    print(f"Optimization rate: {context_stats['optimization_rate']:.1%}")
    print(f"Average optimization time: {context_stats['avg_optimization_time']*1000:.1f}ms")
    
    # Benchmark performance
    print("\n🏁 PERFORMANCE BENCHMARK")
    print("=" * 40)
    
    benchmark_results = enhanced_detector.benchmark_context_optimization(test_cases)
    print(f"Tests run: {benchmark_results['test_count']}")
    print(f"Optimizations used: {benchmark_results['optimization_used_count']}")
    print(f"Average improvement: {benchmark_results['avg_improvement_score']:.3f}")
    print(f"Processing overhead: {benchmark_results['avg_overhead_ms']:.1f}ms ({benchmark_results['overhead_percentage']:.1f}%)")
    
    return enhanced_detector, benchmark_results


if __name__ == "__main__":
    demo_context_enhanced_detector()