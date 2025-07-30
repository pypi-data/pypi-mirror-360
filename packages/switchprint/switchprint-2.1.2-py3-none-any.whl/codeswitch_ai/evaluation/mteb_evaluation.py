#!/usr/bin/env python3
"""MTEB (Massive Text Embedding Benchmark) evaluation integration."""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import time
from collections import defaultdict

try:
    import mteb
    from mteb import MTEB
    from mteb.tasks import *
    MTEB_AVAILABLE = True
except ImportError:
    MTEB_AVAILABLE = False
    print("⚠ MTEB not available. Install with: pip install mteb")

from sentence_transformers import SentenceTransformer
import torch
try:
    from ..detection.ensemble_detector import EnsembleDetector
    from ..detection.transformer_detector import TransformerDetector
    DETECTORS_AVAILABLE = True
except ImportError:
    DETECTORS_AVAILABLE = False

try:
    from ..memory.embedding_generator import EmbeddingGenerator
    EMBEDDING_GENERATOR_AVAILABLE = True
except ImportError:
    EMBEDDING_GENERATOR_AVAILABLE = False


@dataclass
class MTEBResults:
    """MTEB evaluation results."""
    task_name: str
    score: float
    scores_per_language: Dict[str, float]
    evaluation_time: float
    model_name: str
    task_type: str
    dataset_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary."""
        return asdict(self)
    
    def summary(self) -> str:
        """Generate summary report."""
        lang_summary = ""
        if self.scores_per_language:
            avg_score = np.mean(list(self.scores_per_language.values()))
            lang_summary = f"\nLanguage-wise avg: {avg_score:.4f}"
            
        return f"""
MTEB Task: {self.task_name}
=========================
Model: {self.model_name}
Task Type: {self.task_type}
Overall Score: {self.score:.4f}{lang_summary}
Dataset Size: {self.dataset_size}
Evaluation Time: {self.evaluation_time:.2f}s
"""


class CodeSwitchingEmbeddingModel:
    """Wrapper for code-switching aware embedding models."""
    
    def __init__(self, base_model: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize with base embedding model.
        
        Args:
            base_model: Base sentence transformer model name
        """
        self.model_name = base_model
        self.base_model = SentenceTransformer(base_model)
        self.detector = EnsembleDetector() if DETECTORS_AVAILABLE else None
        
        # Code-switching enhancement layer
        self.cs_weights = {
            'monolingual': 1.0,
            'code_switched': 1.1,  # Slight boost for code-switched content
            'multilingual': 1.05
        }
    
    def encode(self, sentences: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Encode sentences with code-switching awareness.
        
        Args:
            sentences: Input sentences
            **kwargs: Additional encoding arguments
            
        Returns:
            Sentence embeddings with code-switching enhancement
        """
        if isinstance(sentences, str):
            sentences = [sentences]
        
        # Get base embeddings
        base_embeddings = self.base_model.encode(sentences, **kwargs)
        
        # Enhance with code-switching detection if available
        if self.detector:
            enhanced_embeddings = []
            for i, sentence in enumerate(sentences):
                try:
                    # Detect code-switching
                    result = self.detector.detect_language(sentence)
                    
                    # Apply enhancement based on code-switching characteristics
                    embedding = base_embeddings[i].copy()
                    
                    if len(result.detected_languages) > 1:
                        # Code-switched content
                        weight = self.cs_weights['code_switched']
                    elif len(result.detected_languages) == 1:
                        # Monolingual content
                        weight = self.cs_weights['monolingual']
                    else:
                        # Multilingual/uncertain
                        weight = self.cs_weights['multilingual']
                    
                    # Apply weight and normalize
                    embedding = embedding * weight
                    embedding = embedding / np.linalg.norm(embedding)
                    enhanced_embeddings.append(embedding)
                    
                except Exception:
                    # Fallback to base embedding
                    enhanced_embeddings.append(base_embeddings[i])
            
            return np.array(enhanced_embeddings)
        
        return base_embeddings


class MTEBEvaluator:
    """MTEB evaluation framework for code-switching models."""
    
    # Code-switching relevant MTEB tasks
    CS_RELEVANT_TASKS = [
        # Multilingual tasks that benefit from code-switching awareness
        "MultilingualSentiment",
        "MultilingualSTS", 
        "XNLI",
        "MLQARetrieval",
        "MultiLongDocRetrieval",
        "XQuADRetrieval",
        "NeuCLIR2023Retrieval",
        "BelebeleRetrieval",
        "FloresSimilarity",
        "BuccRetrieval",
        "DiaBLaRetrieval",
        "WikipediaRetrieval",
        "ArguAna",
        "ClimateFEVER",
        "DBPedia",
        "FEVER",
        "FiQA2018",
        "HotpotQA",
        "MSMARCO",
        "NFCorpus",
        "NQ",
        "QuoraRetrieval",
        "SCIDOCS",
        "SciFact",
        "Touche2020",
        "TRECCOVID",
    ]
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2", 
                 cache_dir: str = ".mteb_cache"):
        """Initialize MTEB evaluator.
        
        Args:
            model_name: Name of base embedding model
            cache_dir: Directory for caching results
        """
        if not MTEB_AVAILABLE:
            raise ImportError("MTEB is required. Install with: pip install mteb")
        
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize code-switching aware model
        self.cs_model = CodeSwitchingEmbeddingModel(model_name)
        
        # Initialize MTEB evaluation
        self.mteb = MTEB()
        
        # Results storage
        self.results = {}
    
    def evaluate_on_task(self, task_name: str, languages: Optional[List[str]] = None) -> Optional[MTEBResults]:
        """Evaluate model on specific MTEB task.
        
        Args:
            task_name: Name of MTEB task
            languages: Optional list of languages to evaluate on
            
        Returns:
            Evaluation results
        """
        if task_name not in self.CS_RELEVANT_TASKS:
            print(f"⚠ Task {task_name} not in code-switching relevant tasks")
            print(f"Available tasks: {self.CS_RELEVANT_TASKS[:5]}...")
        
        print(f"🔬 Evaluating {self.model_name} on {task_name}")
        
        try:
            # Load task
            task = self.mteb.get_task(task_name)
            
            # Set up evaluation parameters
            eval_params = {}
            if languages:
                eval_params['languages'] = languages
            
            # Run evaluation
            start_time = time.time()
            
            # MTEB expects the model to have .encode() method
            results = self.mteb.run(
                model=self.cs_model,
                tasks=[task_name],
                output_folder=str(self.cache_dir),
                **eval_params
            )
            
            eval_time = time.time() - start_time
            
            # Process results
            task_results = results[0] if results else None
            if not task_results:
                print(f"❌ No results for {task_name}")
                return None
            
            # Extract scores
            main_score = task_results.get('main_score', 0.0)
            scores_per_lang = task_results.get('scores_per_language', {})
            
            # Get task metadata
            task_type = getattr(task, 'task_type', 'unknown')
            dataset_size = getattr(task, 'dataset_size', 0)
            
            mteb_result = MTEBResults(
                task_name=task_name,
                score=main_score,
                scores_per_language=scores_per_lang,
                evaluation_time=eval_time,
                model_name=self.model_name,
                task_type=task_type,
                dataset_size=dataset_size
            )
            
            # Cache results
            self.results[task_name] = mteb_result
            
            print(f"✓ {task_name}: {main_score:.4f} ({eval_time:.1f}s)")
            return mteb_result
            
        except Exception as e:
            print(f"❌ Failed to evaluate {task_name}: {e}")
            return None
    
    def run_comprehensive_evaluation(self, max_tasks: int = 10, 
                                   languages: Optional[List[str]] = None) -> Dict[str, MTEBResults]:
        """Run comprehensive evaluation on multiple MTEB tasks.
        
        Args:
            max_tasks: Maximum number of tasks to evaluate
            languages: Optional list of languages
            
        Returns:
            Dictionary of task results
        """
        print(f"🚀 Running comprehensive MTEB evaluation")
        print(f"Model: {self.model_name}")
        print(f"Max tasks: {max_tasks}")
        
        # Select tasks to evaluate
        tasks_to_run = self.CS_RELEVANT_TASKS[:max_tasks]
        
        results = {}
        total_time = 0
        
        for i, task_name in enumerate(tasks_to_run, 1):
            print(f"\n[{i}/{len(tasks_to_run)}] Evaluating {task_name}")
            
            result = self.evaluate_on_task(task_name, languages)
            if result:
                results[task_name] = result
                total_time += result.evaluation_time
            
            # Progress update
            if i % 3 == 0:
                avg_score = np.mean([r.score for r in results.values()]) if results else 0
                print(f"📊 Progress: {i}/{len(tasks_to_run)} | Avg Score: {avg_score:.4f}")
        
        print(f"\n✓ Comprehensive evaluation completed in {total_time:.1f}s")
        print(f"Tasks completed: {len(results)}/{len(tasks_to_run)}")
        
        self.results.update(results)
        return results
    
    def generate_report(self, results: Optional[Dict[str, MTEBResults]] = None) -> str:
        """Generate comprehensive evaluation report.
        
        Args:
            results: Optional results dict, uses self.results if None
            
        Returns:
            Formatted report string
        """
        if results is None:
            results = self.results
        
        if not results:
            return "No MTEB evaluation results available."
        
        report = [
            "MTEB Evaluation Report for Code-Switching Models",
            "=" * 60,
            f"Model: {self.model_name}",
            f"Tasks Evaluated: {len(results)}",
            ""
        ]
        
        # Summary statistics
        all_scores = [r.score for r in results.values()]
        if all_scores:
            report.extend([
                "Summary Statistics:",
                "-" * 20,
                f"Average Score: {np.mean(all_scores):.4f}",
                f"Median Score:  {np.median(all_scores):.4f}",
                f"Best Score:    {np.max(all_scores):.4f}",
                f"Worst Score:   {np.min(all_scores):.4f}",
                f"Std Dev:       {np.std(all_scores):.4f}",
                ""
            ])
        
        # Task-wise results
        report.append("Task-wise Results:")
        report.append("-" * 20)
        
        # Sort by score (descending)
        sorted_results = sorted(results.items(), key=lambda x: x[1].score, reverse=True)
        
        for task_name, result in sorted_results:
            eval_time_str = f"({result.evaluation_time:.1f}s)"
            report.append(f"{task_name:25s}: {result.score:.4f} {eval_time_str}")
        
        # Performance by task type
        task_types = defaultdict(list)
        for result in results.values():
            task_types[result.task_type].append(result.score)
        
        if len(task_types) > 1:
            report.extend([
                "",
                "Performance by Task Type:",
                "-" * 25
            ])
            
            for task_type, scores in task_types.items():
                avg_score = np.mean(scores)
                count = len(scores)
                report.append(f"{task_type:20s}: {avg_score:.4f} ({count} tasks)")
        
        # Detailed results
        report.extend([
            "",
            "Detailed Results:",
            "-" * 16
        ])
        
        for task_name, result in sorted_results:
            report.append(result.summary())
        
        return "\n".join(report)
    
    def save_results(self, output_file: str = "mteb_evaluation_results.json"):
        """Save evaluation results to file.
        
        Args:
            output_file: Output file path
        """
        if not self.results:
            print("⚠ No results to save")
            return
        
        # Convert to serializable format
        serializable_results = {}
        for task_name, result in self.results.items():
            serializable_results[task_name] = result.to_dict()
        
        # Add metadata
        output_data = {
            'model_name': self.model_name,
            'evaluation_timestamp': time.time(),
            'num_tasks': len(self.results),
            'results': serializable_results
        }
        
        output_path = self.cache_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✓ MTEB results saved to {output_path}")
    
    def benchmark_against_baseline(self, baseline_results: Dict[str, float]) -> Dict[str, float]:
        """Compare results against baseline model.
        
        Args:
            baseline_results: Dictionary of {task_name: score} for baseline
            
        Returns:
            Dictionary of improvements {task_name: improvement}
        """
        improvements = {}
        
        for task_name, result in self.results.items():
            if task_name in baseline_results:
                baseline_score = baseline_results[task_name]
                improvement = result.score - baseline_score
                improvements[task_name] = improvement
        
        return improvements


def main():
    """Example usage of MTEB evaluator."""
    if not MTEB_AVAILABLE:
        print("❌ MTEB not available. Install with: pip install mteb")
        return
    
    # Initialize evaluator
    evaluator = MTEBEvaluator()
    
    # Run evaluation on subset of tasks (for demo)
    results = evaluator.run_comprehensive_evaluation(max_tasks=3)
    
    # Generate and save report
    report = evaluator.generate_report(results)
    print(report)
    
    evaluator.save_results()


if __name__ == "__main__":
    main()