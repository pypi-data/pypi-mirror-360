#!/usr/bin/env python3
"""
High-Performance Batch Processing for Code-Switching Detection

Optimizes detection for high-throughput applications with:
1. Parallel processing with optimal thread/process management
2. Intelligent caching and deduplication
3. Memory-efficient streaming processing
4. Adaptive batch sizing based on system resources
5. Progress tracking and error handling
6. Performance profiling and optimization
"""

import os
import time
import hashlib
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Optional, Any, Union, Callable, Iterator
from dataclasses import dataclass, asdict
import threading
from pathlib import Path
import json
import pickle
from functools import lru_cache
import psutil

from ..analysis.integrated_detector import IntegratedImprovedDetector, IntegratedResult


@dataclass
class BatchConfig:
    """Configuration for batch processing optimization."""
    max_workers: Optional[int] = None          # Auto-detect optimal workers
    use_multiprocessing: bool = False          # Thread vs process parallelization
    enable_caching: bool = True                # Cache identical texts
    cache_size: int = 10000                   # LRU cache size
    chunk_size: int = 100                     # Texts per chunk
    memory_limit_mb: int = 1024               # Memory usage limit
    progress_interval: int = 50               # Progress update frequency
    error_handling: str = "continue"          # continue, stop, collect
    save_intermediate: bool = False           # Save progress checkpoints
    checkpoint_interval: int = 1000          # Checkpoint frequency


@dataclass
class BatchMetrics:
    """Metrics for batch processing performance."""
    total_texts: int
    processed_texts: int
    failed_texts: int
    total_time: float
    avg_time_per_text: float
    texts_per_second: float
    cache_hits: int
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    worker_efficiency: float


@dataclass 
class BatchResult:
    """Result of batch processing operation."""
    results: List[IntegratedResult]
    failed_indices: List[int]
    metrics: BatchMetrics
    config: BatchConfig


class HighPerformanceBatchProcessor:
    """Optimized batch processor for high-throughput detection."""
    
    def __init__(self, detector: Optional[IntegratedImprovedDetector] = None,
                 config: Optional[BatchConfig] = None):
        """Initialize batch processor with optimization settings."""
        
        self.detector = detector or IntegratedImprovedDetector(
            performance_mode="fast",  # Default to fast mode for batch
            auto_train_calibration=False  # Skip training for batch speed
        )
        
        self.config = config or BatchConfig()
        self._setup_optimal_config()
        
        # Performance tracking
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.processing_times = []
        
        # Thread safety
        self.cache_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        print(f"🚀 High-Performance Batch Processor initialized")
        print(f"   Workers: {self.config.max_workers}, Caching: {self.config.enable_caching}")
        print(f"   Memory limit: {self.config.memory_limit_mb}MB, Chunk size: {self.config.chunk_size}")
    
    def _setup_optimal_config(self):
        """Auto-configure optimal settings based on system resources."""
        
        # Auto-detect optimal worker count
        if self.config.max_workers is None:
            cpu_count = os.cpu_count() or 4
            # For I/O bound tasks (language detection), use more threads
            self.config.max_workers = min(cpu_count * 2, 16)
        
        # Adjust chunk size based on memory
        available_memory = psutil.virtual_memory().available / (1024**2)  # MB
        if available_memory < 2048:  # Less than 2GB
            self.config.chunk_size = 50
            self.config.cache_size = 5000
        elif available_memory > 8192:  # More than 8GB
            self.config.chunk_size = 200
            self.config.cache_size = 20000
        
        print(f"🔧 Auto-configured for system: {available_memory:.0f}MB RAM, {os.cpu_count()} CPUs")
    
    def process_batch(self, texts: List[str], 
                     checkpoint_file: Optional[str] = None) -> BatchResult:
        """Process batch of texts with full optimization."""
        
        start_time = time.time()
        total_texts = len(texts)
        
        print(f"📊 Starting batch processing: {total_texts:,} texts")
        print(f"   Configuration: {self.config.max_workers} workers, {self.config.chunk_size} chunk size")
        
        # Load checkpoint if exists
        completed_indices = set()
        results = [None] * total_texts
        
        if checkpoint_file and Path(checkpoint_file).exists():
            completed_indices, results = self._load_checkpoint(checkpoint_file)
            print(f"📁 Resumed from checkpoint: {len(completed_indices)} completed")
        
        # Filter out already completed texts
        pending_work = [(i, text) for i, text in enumerate(texts) 
                       if i not in completed_indices]
        
        if not pending_work:
            print("✅ All texts already processed from checkpoint")
            return self._create_batch_result(results, [], start_time, total_texts)
        
        # Process in chunks with optimal parallelization
        failed_indices = []
        
        if self.config.use_multiprocessing:
            processed_results, failures = self._process_with_multiprocessing(pending_work)
        else:
            processed_results, failures = self._process_with_threading(pending_work)
        
        # Merge results
        for idx, result in processed_results:
            results[idx] = result
        
        failed_indices.extend(failures)
        
        # Save final checkpoint
        if checkpoint_file and self.config.save_intermediate:
            self._save_checkpoint(checkpoint_file, set(range(total_texts)), results)
        
        end_time = time.time()
        
        # Calculate metrics
        metrics = self._calculate_metrics(total_texts, len(failed_indices), 
                                        end_time - start_time)
        
        print(f"🎉 Batch processing complete!")
        print(f"   Processed: {total_texts - len(failed_indices):,}/{total_texts:,} texts")
        print(f"   Speed: {metrics.texts_per_second:.1f} texts/sec")
        print(f"   Cache hit rate: {metrics.cache_hit_rate:.1%}")
        
        return BatchResult(
            results=[r for r in results if r is not None],
            failed_indices=failed_indices,
            metrics=metrics,
            config=self.config
        )
    
    def _process_with_threading(self, work_items: List[tuple]) -> tuple:
        """Process using thread-based parallelization."""
        
        processed_results = []
        failed_indices = []
        
        # Split into chunks for better memory management
        chunks = [work_items[i:i + self.config.chunk_size] 
                 for i in range(0, len(work_items), self.config.chunk_size)]
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit chunks
            chunk_futures = []
            for chunk_idx, chunk in enumerate(chunks):
                future = executor.submit(self._process_chunk, chunk, chunk_idx)
                chunk_futures.append(future)
            
            # Collect results as they complete
            for future in as_completed(chunk_futures):
                try:
                    chunk_results, chunk_failures = future.result()
                    processed_results.extend(chunk_results)
                    failed_indices.extend(chunk_failures)
                except Exception as e:
                    print(f"⚠️ Chunk processing failed: {e}")
        
        return processed_results, failed_indices
    
    def _process_with_multiprocessing(self, work_items: List[tuple]) -> tuple:
        """Process using process-based parallelization."""
        
        # Note: Multiprocessing requires picklable objects
        # For now, fall back to threading for simplicity
        print("📝 Multiprocessing fallback to threading (detector not picklable)")
        return self._process_with_threading(work_items)
    
    def _process_chunk(self, chunk: List[tuple], chunk_idx: int) -> tuple:
        """Process a chunk of texts."""
        
        chunk_results = []
        chunk_failures = []
        
        for i, (text_idx, text) in enumerate(chunk):
            try:
                # Progress tracking
                if (i + 1) % self.config.progress_interval == 0:
                    print(f"   Chunk {chunk_idx}: {i + 1}/{len(chunk)} texts processed")
                
                # Check cache first
                result = self._get_cached_result(text)
                if result is None:
                    # Process text
                    start_time = time.time()
                    result = self.detector.detect_language(text)
                    processing_time = time.time() - start_time
                    
                    # Cache result
                    self._cache_result(text, result)
                    
                    # Track timing
                    with self.stats_lock:
                        self.processing_times.append(processing_time)
                
                chunk_results.append((text_idx, result))
                
            except Exception as e:
                print(f"⚠️ Failed to process text {text_idx}: {str(e)[:100]}")
                chunk_failures.append(text_idx)
                
                if self.config.error_handling == "stop":
                    raise
        
        return chunk_results, chunk_failures
    
    def _get_cached_result(self, text: str) -> Optional[IntegratedResult]:
        """Get cached result for text if available."""
        
        if not self.config.enable_caching:
            return None
        
        # Create hash key for text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        with self.cache_lock:
            if text_hash in self.cache:
                self.cache_hits += 1
                return self.cache[text_hash]
            else:
                self.cache_misses += 1
                return None
    
    def _cache_result(self, text: str, result: IntegratedResult):
        """Cache processing result."""
        
        if not self.config.enable_caching:
            return
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        with self.cache_lock:
            # Implement LRU eviction if cache is full
            if len(self.cache) >= self.config.cache_size:
                # Remove oldest entry (simple FIFO for now)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[text_hash] = result
    
    def _save_checkpoint(self, filename: str, completed_indices: set, results: List):
        """Save processing checkpoint."""
        
        checkpoint_data = {
            'completed_indices': list(completed_indices),
            'results': [asdict(result) if result else None for result in results],
            'timestamp': time.time()
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        print(f"💾 Checkpoint saved: {len(completed_indices)} completed")
    
    def _load_checkpoint(self, filename: str) -> tuple:
        """Load processing checkpoint."""
        
        with open(filename, 'rb') as f:
            checkpoint_data = pickle.load(f)
        
        completed_indices = set(checkpoint_data['completed_indices'])
        
        # Reconstruct results (simplified for demo)
        results = checkpoint_data['results']
        
        return completed_indices, results
    
    def _calculate_metrics(self, total_texts: int, failed_count: int, 
                         total_time: float) -> BatchMetrics:
        """Calculate comprehensive processing metrics."""
        
        processed_count = total_texts - failed_count
        
        # Performance metrics
        avg_time = total_time / max(1, processed_count)
        texts_per_sec = processed_count / max(0.001, total_time)
        
        # Cache metrics
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / max(1, total_requests)
        
        # System metrics
        memory_usage = psutil.Process().memory_info().rss / (1024**2)  # MB
        cpu_usage = psutil.cpu_percent()
        
        # Worker efficiency (simplified)
        theoretical_max_speed = self.config.max_workers * (1 / max(0.001, avg_time))
        worker_efficiency = min(1.0, texts_per_sec / max(0.001, theoretical_max_speed))
        
        return BatchMetrics(
            total_texts=total_texts,
            processed_texts=processed_count,
            failed_texts=failed_count,
            total_time=total_time,
            avg_time_per_text=avg_time,
            texts_per_second=texts_per_sec,
            cache_hits=self.cache_hits,
            cache_hit_rate=cache_hit_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            worker_efficiency=worker_efficiency
        )
    
    def _create_batch_result(self, results: List, failed_indices: List,
                           start_time: float, total_texts: int) -> BatchResult:
        """Create batch result from processed data."""
        
        total_time = time.time() - start_time
        metrics = self._calculate_metrics(total_texts, len(failed_indices), total_time)
        
        return BatchResult(
            results=[r for r in results if r is not None],
            failed_indices=failed_indices,
            metrics=metrics,
            config=self.config
        )
    
    def process_stream(self, text_stream: Iterator[str], 
                      output_callback: Callable[[IntegratedResult], None],
                      buffer_size: int = 1000) -> BatchMetrics:
        """Process streaming text data with memory efficiency."""
        
        print("🌊 Starting streaming processing...")
        
        start_time = time.time()
        processed_count = 0
        failed_count = 0
        buffer = []
        
        try:
            for text in text_stream:
                buffer.append(text)
                
                # Process buffer when full
                if len(buffer) >= buffer_size:
                    batch_result = self.process_batch(buffer)
                    
                    # Send results to callback
                    for result in batch_result.results:
                        output_callback(result)
                    
                    processed_count += len(batch_result.results)
                    failed_count += len(batch_result.failed_indices)
                    
                    # Clear buffer
                    buffer.clear()
                    
                    print(f"   Processed {processed_count:,} texts so far...")
            
            # Process remaining buffer
            if buffer:
                batch_result = self.process_batch(buffer)
                for result in batch_result.results:
                    output_callback(result)
                processed_count += len(batch_result.results)
                failed_count += len(batch_result.failed_indices)
        
        except Exception as e:
            print(f"⚠️ Streaming processing error: {e}")
            failed_count += len(buffer)
        
        total_time = time.time() - start_time
        metrics = self._calculate_metrics(processed_count + failed_count, 
                                        failed_count, total_time)
        
        print(f"🎉 Streaming complete: {processed_count:,} texts processed")
        return metrics
    
    def benchmark_performance(self, test_texts: List[str]) -> Dict[str, Any]:
        """Benchmark different configuration options."""
        
        print("🏁 Benchmarking batch processing configurations...")
        
        configs_to_test = [
            BatchConfig(max_workers=1, chunk_size=50, enable_caching=False),
            BatchConfig(max_workers=4, chunk_size=100, enable_caching=True),
            BatchConfig(max_workers=8, chunk_size=200, enable_caching=True),
            BatchConfig(max_workers=self.config.max_workers, 
                       chunk_size=self.config.chunk_size, enable_caching=True)
        ]
        
        benchmark_results = {}
        
        for i, config in enumerate(configs_to_test):
            print(f"\n📊 Testing configuration {i+1}/{len(configs_to_test)}")
            
            # Create processor with test config
            processor = HighPerformanceBatchProcessor(self.detector, config)
            
            # Run benchmark
            start_time = time.time()
            result = processor.process_batch(test_texts[:100])  # Use subset for speed
            runtime = time.time() - start_time
            
            benchmark_results[f"config_{i+1}"] = {
                'config': asdict(config),
                'texts_per_second': result.metrics.texts_per_second,
                'cache_hit_rate': result.metrics.cache_hit_rate,
                'memory_usage_mb': result.metrics.memory_usage_mb,
                'runtime_seconds': runtime
            }
            
            print(f"   Speed: {result.metrics.texts_per_second:.1f} texts/sec")
        
        # Find best configuration
        best_config = max(benchmark_results.items(), 
                         key=lambda x: x[1]['texts_per_second'])
        
        print(f"\n🏆 Best configuration: {best_config[0]}")
        print(f"   Speed: {best_config[1]['texts_per_second']:.1f} texts/sec")
        
        return benchmark_results


def demo_batch_processing():
    """Demonstrate high-performance batch processing."""
    
    print("🚀 BATCH PROCESSING DEMO")
    print("=" * 50)
    
    # Create test dataset
    test_texts = [
        "Hello world",
        "Hola mundo", 
        "Bonjour le monde",
        "I need chai right now",
        "Yallah chalein",
        "Hello, ¿cómo estás? I am doing bien today",
        "Je suis très tired aujourd'hui",
        "Main ghar ja raha hoon but I'll be back",
        "这个很好 but I think we need more tiempo",
        "Привет! How are you doing сегодня?"
    ] * 100  # Repeat for realistic batch size
    
    print(f"📝 Processing {len(test_texts):,} texts...")
    
    # Create optimized batch processor
    config = BatchConfig(
        max_workers=8,
        chunk_size=100,
        enable_caching=True,
        progress_interval=100
    )
    
    processor = HighPerformanceBatchProcessor(config=config)
    
    # Process batch
    start_time = time.time()
    result = processor.process_batch(test_texts)
    total_time = time.time() - start_time
    
    print(f"\n📊 Results Summary:")
    print(f"   Total texts: {result.metrics.total_texts:,}")
    print(f"   Processed: {result.metrics.processed_texts:,}")
    print(f"   Failed: {result.metrics.failed_texts}")
    print(f"   Speed: {result.metrics.texts_per_second:.1f} texts/sec")
    print(f"   Cache hit rate: {result.metrics.cache_hit_rate:.1%}")
    print(f"   Memory usage: {result.metrics.memory_usage_mb:.1f} MB")
    print(f"   Worker efficiency: {result.metrics.worker_efficiency:.1%}")
    
    # Benchmark different configurations
    benchmark_results = processor.benchmark_performance(test_texts[:500])
    
    return processor, result, benchmark_results


if __name__ == "__main__":
    demo_batch_processing()