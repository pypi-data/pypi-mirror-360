"""
Optimization Module for SwitchPrint

Provides advanced optimization features for improving code-switching detection
performance through context analysis, window optimization, and adaptive algorithms.
"""

from .context_window import (
    ContextWindowOptimizer,
    ContextConfig,
    ContextualWordAnalysis,
    ContextOptimizationResult,
    TextType
)

__all__ = [
    'ContextWindowOptimizer',
    'ContextConfig',
    'ContextualWordAnalysis', 
    'ContextOptimizationResult',
    'TextType'
]