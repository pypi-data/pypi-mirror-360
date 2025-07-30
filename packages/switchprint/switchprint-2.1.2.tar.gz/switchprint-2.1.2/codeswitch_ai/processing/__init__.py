"""
High-Performance Processing Module for SwitchPrint

Provides optimized batch processing and streaming capabilities for
high-throughput code-switching detection applications.
"""

from .batch_processor import (
    HighPerformanceBatchProcessor,
    BatchConfig,
    BatchMetrics,
    BatchResult
)

__all__ = [
    'HighPerformanceBatchProcessor',
    'BatchConfig', 
    'BatchMetrics',
    'BatchResult'
]