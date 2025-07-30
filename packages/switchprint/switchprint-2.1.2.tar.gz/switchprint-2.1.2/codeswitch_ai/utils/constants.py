"""Constants and configuration for the SwitchPrint Library."""

# Version information
VERSION = "2.1.1"
AUTHOR = "Aahad Vakani"
PYPI_URL = "https://pypi.org/project/switchprint/"
PACKAGE_NAME = "switchprint"

# Performance thresholds
CONFIDENCE_THRESHOLDS = {
    'high': 0.85,     # Function words, native scripts
    'medium': 0.6,    # Pattern matches, user languages
    'low': 0.4        # Romanization, fallback detection
}

# Context window settings for adaptive analysis
CONTEXT_WINDOWS = {
    'very_short': {'min_length': 1, 'max_length': 1, 'text_threshold': 5},
    'short': {'min_length': 2, 'max_length': 3, 'text_threshold': 15},
    'medium': {'min_length': 2, 'max_length': 4, 'text_threshold': 30},
    'long': {'min_length': 3, 'max_length': 5, 'text_threshold': float('inf')}
}

# Cache settings
CACHE_SETTINGS = {
    'max_size': 500,
    'ttl_minutes': 15,
    'cleanup_threshold': 0.8
}

# Supported language families
LANGUAGE_FAMILIES = {
    'european': ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'sv', 'no', 'da', 'fi'],
    'slavic': ['ru', 'pl', 'cs', 'sk', 'hr', 'sr', 'bg', 'sl'],
    'south_asian': ['hi', 'ur', 'bn', 'ta', 'te', 'gu', 'mr', 'pa'],
    'east_asian': ['zh', 'ja', 'ko'],
    'southeast_asian': ['id', 'ms', 'tl', 'th', 'vi'],
    'african': ['sw', 'xh', 'zu', 'yo', 'ig', 'ha'],
    'middle_eastern': ['ar', 'fa', 'he', 'tr'],
    'indigenous': ['mi', 'haw', 'cr', 'lkt']
}

# Script confidence multipliers
SCRIPT_CONFIDENCE_MULTIPLIERS = {
    'ur': 1.2, 'hi': 1.1, 'ar': 1.1, 'fa': 1.1, 'tr': 1.05,
    'en': 1.0, 'es': 1.0, 'fr': 1.0, 'de': 1.0, 'it': 1.0, 'pt': 1.0
}

# Native script detection threshold
NATIVE_SCRIPT_THRESHOLD = 0.2  # 20% of text must be in native script

# Performance tracking (v2.0.0 achieved targets)
PERFORMANCE_TARGETS = {
    'accuracy': {
        'overall': 0.8598,          # Achieved: 85.98% (FastText)
        'underserved': 0.70,        # Target for romanized languages
        'function_words': 0.90,     # High accuracy for common words
        'native_scripts': 0.95      # Excellent for native scripts
    },
    'speed': {
        'fasttext_max_ms': 0.6,     # Achieved: 0.1-0.6ms
        'ensemble_max_ms': 100,     # Achieved: 40-70ms
        'transformer_max_ms': 600,  # Achieved: 40-600ms
        'cache_speedup_min': 2.0    # Achieved: 2-5x speedup
    },
    'coverage': {
        'language_families': 8,     # Achieved: 8 major families
        'total_languages': 176,     # Achieved: 176 languages (FastText)
        'multilingual_support': 50  # Achieved: 50+ (sentence-transformers)
    }
}

# Error messages
ERROR_MESSAGES = {
    'empty_text': "Input text is empty or contains only whitespace",
    'invalid_language': "Invalid language code provided",
    'model_load_failed': "Failed to load language detection model",
    'cache_error': "Cache operation failed",
    'embedding_error': "Embedding generation failed"
}

# Default settings for components
DEFAULT_SETTINGS = {
    'language_detector': {
        'confidence_threshold': 0.7,
        'minimum_text_length': 3,
        'seed': 0
    },
    'enhanced_detector': {
        'min_segment_length': 3,
        'context_window': 10,
        'confidence_threshold': 0.6
    },
    'optimized_detector': {
        'high_confidence_threshold': 0.85,
        'medium_confidence_threshold': 0.6,
        'low_confidence_threshold': 0.4
    },
    'embedding_generator': {
        'model_name': 'paraphrase-multilingual-MiniLM-L12-v2',  # Enhanced v2.0.0
        'normalize_embeddings': True
    },
    'conversation_memory': {
        'max_conversations': 10000,
        'cleanup_interval_days': 90
    }
}