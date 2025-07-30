#!/usr/bin/env python3
"""
Error Analysis Framework for Code-Switching Detection

Systematic analysis of failure cases to identify improvement opportunities
and push performance from current 0.643 F1 toward academic benchmarks (0.80+).
"""

import re
import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns

from ..detection.general_cs_detector import GeneralCodeSwitchingDetector, GeneralCSResult, WordAnalysis


@dataclass
class ErrorCase:
    """Individual error case for analysis."""
    text: str
    expected_languages: List[str]
    predicted_languages: List[str]
    expected_switches: int
    predicted_switches: int
    confidence: float
    error_type: str
    language_pairs: List[str]
    text_length: int
    word_count: int
    failure_reason: str


@dataclass
class ErrorPattern:
    """Pattern of errors for systematic analysis."""
    pattern_type: str
    frequency: int
    examples: List[ErrorCase]
    languages_affected: List[str]
    confidence_range: Tuple[float, float]
    improvement_suggestion: str


@dataclass
class ErrorAnalysisResult:
    """Comprehensive error analysis results."""
    total_cases: int
    error_cases: List[ErrorCase]
    error_patterns: List[ErrorPattern]
    accuracy_by_language: Dict[str, float]
    accuracy_by_length: Dict[str, float]
    switch_detection_accuracy: float
    confidence_calibration: Dict[str, Any]
    recommendations: List[str]


class ErrorAnalyzer:
    """Systematic error analysis for code-switching detection."""
    
    def __init__(self, detector: Optional[GeneralCodeSwitchingDetector] = None):
        """Initialize error analyzer with detector."""
        self.detector = detector or GeneralCodeSwitchingDetector(
            performance_mode="accurate",  # Use most accurate mode for analysis
            detector_mode="code_switching"
        )
        
        # Error categorization
        self.error_types = {
            "false_positive_cs": "Detected code-switching where none exists",
            "false_negative_cs": "Missed actual code-switching",
            "wrong_language": "Correct switch detection but wrong language",
            "switch_boundary": "Incorrect switch point boundaries",
            "confidence_mismatch": "High confidence on wrong prediction",
            "low_confidence": "Correct prediction but low confidence"
        }
        
    def analyze_test_set(self, test_cases: List[Dict[str, Any]]) -> ErrorAnalysisResult:
        """Analyze a test set and identify error patterns.
        
        Args:
            test_cases: List of test cases with 'text', 'expected_languages', 'expected_switches'
            
        Returns:
            ErrorAnalysisResult with comprehensive analysis
        """
        print(f"🔍 Analyzing {len(test_cases)} test cases...")
        
        error_cases = []
        correct_cases = []
        
        # Process each test case
        for i, test_case in enumerate(test_cases):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(test_cases)} cases...")
                
            result = self.detector.detect_language(test_case['text'])
            
            # Determine if this is an error case
            error_case = self._classify_result(test_case, result)
            
            if error_case:
                error_cases.append(error_case)
            else:
                correct_cases.append((test_case, result))
        
        print(f"✓ Found {len(error_cases)} error cases out of {len(test_cases)} total")
        
        # Analyze error patterns
        error_patterns = self._identify_error_patterns(error_cases)
        
        # Calculate accuracy metrics
        accuracy_metrics = self._calculate_accuracy_metrics(test_cases, error_cases)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(error_patterns, accuracy_metrics)
        
        return ErrorAnalysisResult(
            total_cases=len(test_cases),
            error_cases=error_cases,
            error_patterns=error_patterns,
            accuracy_by_language=accuracy_metrics['by_language'],
            accuracy_by_length=accuracy_metrics['by_length'],
            switch_detection_accuracy=accuracy_metrics['switch_accuracy'],
            confidence_calibration=accuracy_metrics['confidence_calibration'],
            recommendations=recommendations
        )
    
    def _classify_result(self, test_case: Dict[str, Any], result: GeneralCSResult) -> Optional[ErrorCase]:
        """Classify a result as error or correct."""
        text = test_case['text']
        expected_langs = set(test_case['expected_languages'])
        predicted_langs = set(result.detected_languages)
        expected_switches = test_case.get('expected_switches', 0)
        predicted_switches = len(result.switch_points)
        
        # Determine error type
        error_type = None
        failure_reason = ""
        
        # Check for language detection errors
        if expected_langs != predicted_langs:
            if len(expected_langs) == 1 and len(predicted_langs) > 1:
                error_type = "false_positive_cs"
                failure_reason = f"Detected CS in monolingual text: {predicted_langs} vs {expected_langs}"
            elif len(expected_langs) > 1 and len(predicted_langs) == 1:
                error_type = "false_negative_cs"
                failure_reason = f"Missed CS detection: {predicted_langs} vs {expected_langs}"
            elif len(expected_langs) == len(predicted_langs):
                error_type = "wrong_language"
                failure_reason = f"Wrong languages: {predicted_langs} vs {expected_langs}"
            else:
                error_type = "language_count_mismatch"
                failure_reason = f"Language count mismatch: {len(predicted_langs)} vs {len(expected_langs)}"
        
        # Check for switch boundary errors
        elif abs(expected_switches - predicted_switches) > 1:  # Allow 1 switch tolerance
            error_type = "switch_boundary"
            failure_reason = f"Switch count mismatch: {predicted_switches} vs {expected_switches}"
        
        # Check for confidence issues
        elif result.confidence < 0.5 and len(expected_langs) == len(predicted_langs):
            error_type = "low_confidence"
            failure_reason = f"Correct detection but low confidence: {result.confidence:.3f}"
        
        # Check for high confidence wrong predictions
        elif result.confidence > 0.8 and expected_langs != predicted_langs:
            error_type = "confidence_mismatch"
            failure_reason = f"High confidence wrong prediction: {result.confidence:.3f}"
        
        # If no error detected, return None
        if not error_type:
            return None
        
        # Create language pairs
        language_pairs = []
        if len(expected_langs) > 1:
            sorted_langs = sorted(expected_langs)
            language_pairs = [f"{sorted_langs[i]}-{sorted_langs[j]}" 
                            for i in range(len(sorted_langs)) 
                            for j in range(i+1, len(sorted_langs))]
        
        return ErrorCase(
            text=text,
            expected_languages=list(expected_langs),
            predicted_languages=list(predicted_langs),
            expected_switches=expected_switches,
            predicted_switches=predicted_switches,
            confidence=result.confidence,
            error_type=error_type,
            language_pairs=language_pairs,
            text_length=len(text),
            word_count=len(text.split()),
            failure_reason=failure_reason
        )
    
    def _identify_error_patterns(self, error_cases: List[ErrorCase]) -> List[ErrorPattern]:
        """Identify patterns in error cases."""
        patterns = []
        
        # Group by error type
        errors_by_type = defaultdict(list)
        for error in error_cases:
            errors_by_type[error.error_type].append(error)
        
        for error_type, cases in errors_by_type.items():
            if len(cases) < 2:  # Skip single cases
                continue
                
            # Analyze languages affected
            languages = set()
            for case in cases:
                languages.update(case.expected_languages)
                languages.update(case.predicted_languages)
            
            # Calculate confidence range
            confidences = [case.confidence for case in cases]
            confidence_range = (min(confidences), max(confidences))
            
            # Generate improvement suggestions
            suggestion = self._generate_pattern_suggestion(error_type, cases)
            
            pattern = ErrorPattern(
                pattern_type=error_type,
                frequency=len(cases),
                examples=cases[:5],  # Keep top 5 examples
                languages_affected=list(languages),
                confidence_range=confidence_range,
                improvement_suggestion=suggestion
            )
            
            patterns.append(pattern)
        
        # Sort by frequency (most common first)
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        
        return patterns
    
    def _generate_pattern_suggestion(self, error_type: str, cases: List[ErrorCase]) -> str:
        """Generate improvement suggestions for error patterns."""
        suggestions = {
            "false_positive_cs": "Increase threshold for code-switching detection or improve monolingual confidence",
            "false_negative_cs": "Decrease threshold for code-switching detection or enhance switch point sensitivity",
            "wrong_language": "Improve language identification accuracy, possibly add more training data",
            "switch_boundary": "Refine switch point detection algorithm, consider linguistic boundaries",
            "confidence_mismatch": "Implement confidence calibration to better align confidence with accuracy",
            "low_confidence": "Improve confidence estimation for correct predictions"
        }
        
        base_suggestion = suggestions.get(error_type, "Analyze specific cases for targeted improvements")
        
        # Add specific details based on cases
        if cases:
            avg_length = np.mean([case.text_length for case in cases])
            common_languages = Counter()
            for case in cases:
                common_languages.update(case.expected_languages)
                common_languages.update(case.predicted_languages)
            
            most_common_lang = common_languages.most_common(1)[0][0] if common_languages else "unknown"
            
            specific_details = f" (Common in {most_common_lang}, avg length: {avg_length:.0f} chars)"
            return base_suggestion + specific_details
        
        return base_suggestion
    
    def _calculate_accuracy_metrics(self, test_cases: List[Dict], error_cases: List[ErrorCase]) -> Dict[str, Any]:
        """Calculate detailed accuracy metrics."""
        
        # Accuracy by language
        language_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Accuracy by text length
        length_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        # Switch detection accuracy
        switch_correct = 0
        switch_total = 0
        
        # Confidence calibration
        confidence_buckets = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        error_set = {(case.text, tuple(case.expected_languages)) for case in error_cases}
        
        for test_case in test_cases:
            text = test_case['text']
            expected_langs = test_case['expected_languages']
            
            # Detect with our system
            result = self.detector.detect_language(text)
            predicted_langs = result.detected_languages
            
            is_correct = (text, tuple(expected_langs)) not in error_set
            
            # By language
            for lang in expected_langs:
                language_accuracy[lang]['total'] += 1
                if is_correct:
                    language_accuracy[lang]['correct'] += 1
            
            # By length
            length_category = self._get_length_category(len(text))
            length_accuracy[length_category]['total'] += 1
            if is_correct:
                length_accuracy[length_category]['correct'] += 1
            
            # Switch detection
            expected_switches = test_case.get('expected_switches', 0)
            predicted_switches = len(result.switch_points)
            switch_total += 1
            if abs(expected_switches - predicted_switches) <= 1:  # Allow 1 switch tolerance
                switch_correct += 1
            
            # Confidence calibration
            confidence_bucket = f"{int(result.confidence * 10) * 10}-{int(result.confidence * 10) * 10 + 10}%"
            confidence_buckets[confidence_bucket]['total'] += 1
            if is_correct:
                confidence_buckets[confidence_bucket]['correct'] += 1
        
        # Convert to percentages
        accuracy_by_language = {
            lang: stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            for lang, stats in language_accuracy.items()
        }
        
        accuracy_by_length = {
            category: stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            for category, stats in length_accuracy.items()
        }
        
        confidence_calibration = {
            bucket: {
                'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
                'count': stats['total']
            }
            for bucket, stats in confidence_buckets.items()
        }
        
        return {
            'by_language': accuracy_by_language,
            'by_length': accuracy_by_length,
            'switch_accuracy': switch_correct / switch_total if switch_total > 0 else 0,
            'confidence_calibration': confidence_calibration
        }
    
    def _get_length_category(self, length: int) -> str:
        """Categorize text by length."""
        if length < 20:
            return "short"
        elif length < 100:
            return "medium"
        else:
            return "long"
    
    def _generate_recommendations(self, patterns: List[ErrorPattern], 
                                accuracy_metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Based on most common error patterns
        if patterns:
            top_pattern = patterns[0]
            recommendations.append(
                f"🎯 Priority: Address '{top_pattern.pattern_type}' errors "
                f"({top_pattern.frequency} cases) - {top_pattern.improvement_suggestion}"
            )
        
        # Based on language accuracy
        lang_accuracy = accuracy_metrics['by_language']
        if lang_accuracy:
            worst_lang = min(lang_accuracy.keys(), key=lambda l: lang_accuracy[l])
            worst_accuracy = lang_accuracy[worst_lang]
            if worst_accuracy < 0.7:
                recommendations.append(
                    f"🌍 Language Focus: Improve {worst_lang} detection "
                    f"(current: {worst_accuracy:.1%}, target: >70%)"
                )
        
        # Based on switch detection
        switch_accuracy = accuracy_metrics['switch_accuracy']
        if switch_accuracy < 0.8:
            recommendations.append(
                f"🔄 Switch Detection: Improve switch point accuracy "
                f"(current: {switch_accuracy:.1%}, target: >80%)"
            )
        
        # Based on confidence calibration
        conf_cal = accuracy_metrics['confidence_calibration']
        high_conf_buckets = [b for b in conf_cal.keys() if b.startswith('8') or b.startswith('9')]
        if high_conf_buckets:
            high_conf_accuracy = np.mean([conf_cal[b]['accuracy'] for b in high_conf_buckets])
            if high_conf_accuracy < 0.9:
                recommendations.append(
                    f"📊 Confidence: Calibrate high-confidence predictions "
                    f"(80-100% confidence accuracy: {high_conf_accuracy:.1%}, target: >90%)"
                )
        
        # General recommendations
        recommendations.extend([
            "🔬 Data: Collect more examples for worst-performing language pairs",
            "⚙️ Tuning: Experiment with language-specific thresholds",
            "🧠 Model: Consider ensemble with specialized models for problem cases"
        ])
        
        return recommendations
    
    def export_analysis(self, result: ErrorAnalysisResult, filename: str = None) -> str:
        """Export error analysis to JSON format."""
        export_data = {
            'summary': {
                'total_cases': result.total_cases,
                'error_count': len(result.error_cases),
                'error_rate': len(result.error_cases) / result.total_cases,
                'switch_detection_accuracy': result.switch_detection_accuracy
            },
            'error_patterns': [asdict(pattern) for pattern in result.error_patterns],
            'accuracy_metrics': {
                'by_language': result.accuracy_by_language,
                'by_length': result.accuracy_by_length,
                'confidence_calibration': result.confidence_calibration
            },
            'recommendations': result.recommendations,
            'error_cases': [asdict(case) for case in result.error_cases[:50]]  # Limit to 50 cases
        }
        
        json_data = json.dumps(export_data, indent=2)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(json_data)
            print(f"📁 Error analysis exported to {filename}")
        
        return json_data
    
    def print_analysis_summary(self, result: ErrorAnalysisResult):
        """Print a comprehensive analysis summary."""
        print("\n🔍 ERROR ANALYSIS SUMMARY")
        print("=" * 50)
        
        # Overall statistics
        error_rate = len(result.error_cases) / result.total_cases
        print(f"📊 Overall Statistics:")
        print(f"  Total Cases: {result.total_cases}")
        print(f"  Error Cases: {len(result.error_cases)}")
        print(f"  Error Rate: {error_rate:.1%}")
        print(f"  Switch Detection Accuracy: {result.switch_detection_accuracy:.1%}")
        
        # Top error patterns
        print(f"\n🎯 Top Error Patterns:")
        for i, pattern in enumerate(result.error_patterns[:3], 1):
            print(f"  {i}. {pattern.pattern_type}: {pattern.frequency} cases")
            print(f"     Languages: {', '.join(pattern.languages_affected[:3])}")
            print(f"     Suggestion: {pattern.improvement_suggestion}")
        
        # Language accuracy
        print(f"\n🌍 Accuracy by Language:")
        sorted_langs = sorted(result.accuracy_by_language.items(), 
                            key=lambda x: x[1], reverse=True)
        for lang, acc in sorted_langs[:5]:
            print(f"  {lang}: {acc:.1%}")
        
        # Recommendations
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "=" * 50)


def create_test_dataset() -> List[Dict[str, Any]]:
    """Create a test dataset for error analysis."""
    return [
        # Monolingual cases
        {"text": "Hello world, how are you today?", "expected_languages": ["en"], "expected_switches": 0},
        {"text": "Hola amigo, ¿cómo estás?", "expected_languages": ["es"], "expected_switches": 0},
        {"text": "Bonjour mon ami, comment allez-vous?", "expected_languages": ["fr"], "expected_switches": 0},
        
        # Simple code-switching
        {"text": "Hello, ¿cómo estás?", "expected_languages": ["en", "es"], "expected_switches": 1},
        {"text": "I love tacos y también pizza", "expected_languages": ["en", "es"], "expected_switches": 2},
        {"text": "Bonjour! How are you?", "expected_languages": ["fr", "en"], "expected_switches": 1},
        
        # Complex code-switching
        {"text": "Going to the mercado to buy groceries", "expected_languages": ["en", "es"], "expected_switches": 1},
        {"text": "My abuela makes the best cookies", "expected_languages": ["en", "es"], "expected_switches": 1},
        {"text": "C'est magnifique! The view is stunning", "expected_languages": ["fr", "en"], "expected_switches": 1},
        
        # Edge cases
        {"text": "OK", "expected_languages": ["en"], "expected_switches": 0},
        {"text": "Sí", "expected_languages": ["es"], "expected_switches": 0},
        {"text": "Hello! 123 test", "expected_languages": ["en"], "expected_switches": 0},
        
        # Multi-language
        {"text": "Hello, bonjour, hola everyone!", "expected_languages": ["en", "fr", "es"], "expected_switches": 3},
        {"text": "I love París, London, and Madrid", "expected_languages": ["en", "es"], "expected_switches": 1},
    ]


def main():
    """Demo error analysis functionality."""
    print("🔍 RUNNING ERROR ANALYSIS DEMO")
    print("=" * 50)
    
    # Create analyzer
    analyzer = ErrorAnalyzer()
    
    # Create test dataset
    test_cases = create_test_dataset()
    print(f"📝 Created {len(test_cases)} test cases")
    
    # Run analysis
    result = analyzer.analyze_test_set(test_cases)
    
    # Print summary
    analyzer.print_analysis_summary(result)
    
    # Export results
    json_data = analyzer.export_analysis(result, "error_analysis_results.json")
    
    return result


if __name__ == "__main__":
    main()