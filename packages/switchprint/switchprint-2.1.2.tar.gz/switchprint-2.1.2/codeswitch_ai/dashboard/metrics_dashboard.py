#!/usr/bin/env python3
"""
Simple Metrics Dashboard for General Code-Switching Detector

Provides observability and performance insights using the export_analysis() function.
Can be used for monitoring, debugging, and optimizing detection performance.
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

from ..detection.general_cs_detector import GeneralCodeSwitchingDetector, GeneralCSResult

@dataclass
class DashboardMetrics:
    """Aggregated metrics for dashboard display."""
    total_detections: int
    avg_processing_time: float
    avg_confidence: float
    language_distribution: Dict[str, int]
    code_switching_rate: float
    switch_points_distribution: Dict[int, int]
    method_effectiveness: Dict[str, float]
    quality_score: float

class MetricsDashboard:
    """Simple metrics dashboard for code-switching detection observability."""
    
    def __init__(self, detector: Optional[GeneralCodeSwitchingDetector] = None):
        """Initialize metrics dashboard.
        
        Args:
            detector: Optional pre-configured detector. If None, creates default.
        """
        self.detector = detector or GeneralCodeSwitchingDetector(performance_mode="balanced")
        self.detection_history: List[Dict[str, Any]] = []
        self.metrics_cache = {}
        
    def analyze_text(self, text: str, record_metrics: bool = True) -> GeneralCSResult:
        """Analyze text and optionally record metrics.
        
        Args:
            text: Text to analyze
            record_metrics: Whether to record metrics for dashboard
            
        Returns:
            GeneralCSResult with detection information
        """
        start_time = time.time()
        result = self.detector.detect_language(text)
        end_time = time.time()
        
        if record_metrics:
            # Export analysis data
            analysis = self.detector.export_analysis(result, include_debug=True)
            analysis['processing_time'] = end_time - start_time
            analysis['timestamp'] = time.time()
            analysis['input_text'] = text
            
            self.detection_history.append(analysis)
            
            # Clear cache to force recomputation
            self.metrics_cache = {}
        
        return result
    
    def get_metrics(self, last_n: Optional[int] = None) -> DashboardMetrics:
        """Get aggregated metrics from detection history.
        
        Args:
            last_n: If specified, only use last N detections
            
        Returns:
            DashboardMetrics with aggregated statistics
        """
        if not self.detection_history:
            return DashboardMetrics(
                total_detections=0, avg_processing_time=0.0, avg_confidence=0.0,
                language_distribution={}, code_switching_rate=0.0,
                switch_points_distribution={}, method_effectiveness={},
                quality_score=0.0
            )
        
        # Get relevant detections
        history = self.detection_history[-last_n:] if last_n else self.detection_history
        
        # Calculate metrics
        total_detections = len(history)
        processing_times = [h['processing_time'] for h in history]
        confidences = [h['detection_result']['confidence'] for h in history]
        
        # Language distribution
        language_dist = defaultdict(int)
        switch_points_dist = defaultdict(int)
        code_switching_count = 0
        method_scores = defaultdict(list)
        
        for detection in history:
            result = detection['detection_result']
            
            # Count languages
            for lang in result['detected_languages']:
                language_dist[lang] += 1
            
            # Count code-switching
            if result['is_code_mixed']:
                code_switching_count += 1
            
            # Switch points distribution
            switch_count = detection['switch_analysis']['switch_count']
            switch_points_dist[switch_count] += 1
            
            # Method effectiveness (if available)
            if 'quality_metrics' in detection:
                quality = detection['quality_metrics']
                if 'method_distribution' in quality:
                    for method, count in quality['method_distribution'].items():
                        method_scores[method].append(result['confidence'])
        
        # Calculate method effectiveness
        method_effectiveness = {}
        for method, scores in method_scores.items():
            method_effectiveness[method] = sum(scores) / len(scores) if scores else 0.0
        
        # Calculate quality score
        quality_score = sum(confidences) / len(confidences) if confidences else 0.0
        
        return DashboardMetrics(
            total_detections=total_detections,
            avg_processing_time=sum(processing_times) / len(processing_times),
            avg_confidence=sum(confidences) / len(confidences),
            language_distribution=dict(language_dist),
            code_switching_rate=code_switching_count / total_detections,
            switch_points_distribution=dict(switch_points_dist),
            method_effectiveness=method_effectiveness,
            quality_score=quality_score
        )
    
    def print_dashboard(self, last_n: Optional[int] = None):
        """Print a text-based dashboard to console.
        
        Args:
            last_n: If specified, only show metrics for last N detections
        """
        metrics = self.get_metrics(last_n)
        
        print("🔬 CODE-SWITCHING DETECTION DASHBOARD")
        print("=" * 50)
        print(f"📊 Total Detections: {metrics.total_detections}")
        print(f"⚡ Avg Processing Time: {metrics.avg_processing_time*1000:.1f}ms")
        print(f"🎯 Avg Confidence: {metrics.avg_confidence:.3f}")
        print(f"🔄 Code-Switching Rate: {metrics.code_switching_rate:.1%}")
        print(f"⭐ Quality Score: {metrics.quality_score:.3f}")
        
        print("\n🌍 LANGUAGE DISTRIBUTION:")
        if metrics.language_distribution:
            for lang, count in sorted(metrics.language_distribution.items(), 
                                    key=lambda x: x[1], reverse=True):
                percentage = (count / metrics.total_detections) * 100
                print(f"  {lang}: {count} ({percentage:.1f}%)")
        else:
            print("  No data available")
        
        print("\n🎯 SWITCH POINTS DISTRIBUTION:")
        if metrics.switch_points_distribution:
            for switch_count, freq in sorted(metrics.switch_points_distribution.items()):
                percentage = (freq / metrics.total_detections) * 100
                print(f"  {switch_count} switches: {freq} texts ({percentage:.1f}%)")
        else:
            print("  No data available")
        
        print("\n🔧 METHOD EFFECTIVENESS:")
        if metrics.method_effectiveness:
            for method, effectiveness in sorted(metrics.method_effectiveness.items(), 
                                              key=lambda x: x[1], reverse=True):
                print(f"  {method}: {effectiveness:.3f}")
        else:
            print("  No data available")
    
    def export_metrics(self, filename: Optional[str] = None) -> str:
        """Export metrics to JSON format.
        
        Args:
            filename: Optional filename to save to
            
        Returns:
            JSON string of metrics data
        """
        metrics = self.get_metrics()
        export_data = {
            "dashboard_metrics": {
                "total_detections": metrics.total_detections,
                "avg_processing_time": metrics.avg_processing_time,
                "avg_confidence": metrics.avg_confidence,
                "language_distribution": metrics.language_distribution,
                "code_switching_rate": metrics.code_switching_rate,
                "switch_points_distribution": metrics.switch_points_distribution,
                "method_effectiveness": metrics.method_effectiveness,
                "quality_score": metrics.quality_score
            },
            "detector_config": {
                "detector_mode": self.detector.detector_mode,
                "performance_mode": self.detector.performance_mode,
                "threshold_mode": self.detector.threshold_config.mode.value,
                "min_confidence": self.detector.min_confidence,
                "word_analysis_enabled": self.detector.enable_word_analysis
            },
            "detection_history": self.detection_history
        }
        
        json_data = json.dumps(export_data, indent=2)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(json_data)
            print(f"📁 Metrics exported to {filename}")
        
        return json_data
    
    def analyze_batch(self, texts: List[str], show_progress: bool = True) -> List[GeneralCSResult]:
        """Analyze a batch of texts and record metrics.
        
        Args:
            texts: List of texts to analyze
            show_progress: Whether to show progress updates
            
        Returns:
            List of GeneralCSResult objects
        """
        results = []
        
        for i, text in enumerate(texts):
            if show_progress and (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(texts)} texts...")
            
            result = self.analyze_text(text, record_metrics=True)
            results.append(result)
        
        if show_progress:
            print(f"✅ Batch analysis complete: {len(texts)} texts processed")
        
        return results
    
    def clear_history(self):
        """Clear detection history and metrics cache."""
        self.detection_history = []
        self.metrics_cache = {}
        print("🗑️ Detection history cleared")

def demo_dashboard():
    """Demo the metrics dashboard functionality."""
    print("🔬 METRICS DASHBOARD DEMO")
    print("=" * 50)
    
    # Create dashboard with fast mode for demo
    dashboard = MetricsDashboard(
        GeneralCodeSwitchingDetector(
            performance_mode="fast",
            detector_mode="code_switching"
        )
    )
    
    # Sample texts for testing
    test_texts = [
        "Hello world!",  # Monolingual English
        "Hola, how are you?",  # Spanish-English
        "Je suis very happy aujourd'hui",  # French-English
        "This is completely English",  # Monolingual English
        "Bonjour mon ami!",  # Monolingual French
        "I love programming and código también",  # English-Spanish
        "Comment ça va today?",  # French-English
        "Guten Tag, nice to meet you",  # German-English
        "Everything is in English here",  # Monolingual English
        "Mixing languages is muy divertido"  # English-Spanish
    ]
    
    print(f"\n📝 Analyzing {len(test_texts)} test texts...")
    
    # Analyze batch
    results = dashboard.analyze_batch(test_texts, show_progress=False)
    
    print("\n" + "="*50)
    print("📊 DASHBOARD RESULTS:")
    dashboard.print_dashboard()
    
    print("\n" + "="*50)
    print("📁 Export sample (first 100 chars):")
    export_data = dashboard.export_metrics()
    print(export_data[:100] + "...")
    
    return dashboard

if __name__ == "__main__":
    demo_dashboard()