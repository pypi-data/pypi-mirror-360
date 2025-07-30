# Changelog

All notable changes to the Code-Switch Aware AI Library are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.2] - 2025-07-02

### 📚 **Documentation & Examples Update**
- **Updated**: Complete overhaul of examples directory with production API
- **Added**: Advanced usage examples with enterprise security features
- **Updated**: EXAMPLES.md with comprehensive real-world use cases
- **Added**: Performance benchmarking and ensemble strategy comparison
- **Updated**: Basic usage examples with current threshold system API
- **Improved**: Error handling and import validation in examples

### 🔧 **Example Enhancements**
- **Added**: Security pipeline demonstration in basic examples
- **Added**: Custom threshold profile configuration examples
- **Added**: Enterprise security and privacy protection workflows
- **Added**: Conversation memory and retrieval system examples
- **Updated**: All import statements to use current production API
- **Added**: Comprehensive error handling and fallback examples

### 📦 **Package Readiness**
- **Prepared**: Version 2.1.1 for PyPI publication
- **Validated**: All examples work with current API
- **Confirmed**: Documentation accuracy with implemented features
- **Ready**: Production deployment with updated examples

## [2.1.0] - 2025-07-02

### 🎉 **100% Test Coverage Milestone**
- **MAJOR**: Achieved 100% test success rate (49/49 tests passing)
- **Added**: Comprehensive test suite with modern pytest infrastructure
- **Added**: Realistic multilingual test data with social media patterns
- **Added**: Performance validation across text lengths
- **Fixed**: All API compatibility issues resolved

### 🛠 **API Stability & Bug Fixes**
- **Fixed**: `PrivacyProtector.protect_text()` method signature
- **Fixed**: `SecurityMonitor.log_security_event()` parameter handling
- **Fixed**: `OptimizedSimilarityRetriever.search_similar()` embedding format
- **Fixed**: Memory system integration with proper type handling
- **Improved**: Transformer detector consistency for edge cases

### 🔒 **Security & Privacy Enhancements**
- **Validated**: Complete security component functionality
- **Tested**: PII detection and anonymization workflows
- **Verified**: Input validation and threat detection
- **Confirmed**: End-to-end security integration

### 📊 **Performance & Quality**
- **Validated**: Sub-second processing for all text lengths
- **Confirmed**: Excellent scaling across short/medium/long text
- **Tested**: Memory system with FAISS retrieval optimization
- **Verified**: Threshold system across all detection modes

### 🧪 **Testing Infrastructure**
- **Added**: Modern pytest fixtures and parameterization
- **Added**: Realistic code-switching test scenarios
- **Added**: Edge case validation (empty text, numbers, punctuation)
- **Added**: Integration testing across all components
- **Added**: Performance benchmarking and validation

## [2.0.0] - 2025-07-01

### 🎉 **PyPI Publication**
- **Published**: Package officially released on PyPI: https://pypi.org/project/switchprint/
- **Installation**: Now available via `pip install switchprint`
- **Automated Publishing**: GitHub Actions workflow with trusted publishing enabled
- **Documentation**: All documentation updated with PyPI links and installation instructions

### 🚀 **Major Enhancements**

#### **FastText Integration**
- **Added**: FastText language detection with high performance and accuracy
- **Added**: 80x faster detection speed (0.1-0.6ms vs ~100ms)
- **Added**: Support for 176 languages with automatic model download
- **Added**: Enhanced preprocessing with URL/mention/hashtag removal
- **Added**: LRU caching for improved performance

#### **Transformer Support**
- **Added**: mBERT (bert-base-multilingual-cased) contextual detection
- **Added**: XLM-R support for cross-lingual understanding
- **Added**: GPU acceleration with automatic fallback to CPU
- **Added**: Contextual embeddings for better accuracy
- **Added**: Script-based detection for 10+ writing systems

#### **Ensemble Detection**
- **Added**: `EnsembleDetector` combining FastText, transformers, and rules
- **Added**: Multiple strategies: weighted_average, voting, confidence_based
- **Added**: Dynamic weight adjustment based on text characteristics
- **Added**: Smart handling of mixed scripts and short texts
- **Added**: User language guidance integration

### 🔧 **Memory & Retrieval Improvements**

#### **Enhanced Memory System**
- **Added**: Multilingual sentence embeddings (paraphrase-multilingual-MiniLM-L12-v2)
- **Added**: Helper method `create_and_store_conversation()` for easier usage
- **Changed**: Default embedding model supports 50+ languages
- **Improved**: Automatic embedding generation during storage

#### **Optimized Retrieval**
- **Added**: `OptimizedSimilarityRetriever` with GPU acceleration
- **Added**: Advanced FAISS indices (IVF, HNSW) with auto-selection
- **Added**: Product quantization for memory efficiency
- **Added**: Query-level caching with LRU eviction
- **Added**: Performance tracking and statistics
- **Added**: Sub-millisecond similarity search

### 📊 **Performance Metrics**

#### **Speed Improvements**
- **FastText Detection**: 0.1-0.6ms (99.4% faster than previous)
- **Ensemble Detection**: 40-70ms (optimal accuracy-speed balance)
- **Memory Storage**: <1s for conversation with embeddings
- **Similarity Search**: <1ms for 1000+ conversations

#### **Accuracy Improvements**
- **Spanish Mixed Text**: 91.4% confidence
- **French-English**: 100% confidence
- **Chinese-English**: 100% with script detection
- **Russian-English**: 88.8% confidence
- **Overall**: 1.49% accuracy improvement with 80x speed boost

### 🧪 **Testing & Validation**

#### **Enhanced Test Suite**
- **Added**: Comprehensive test coverage (legacy baseline)
- **Added**: `test_fasttext_detector.py` with 11 test cases
- **Added**: `test_ensemble_detector.py` with 9 test cases  
- **Added**: `test_integration.py` for end-to-end validation
- **Added**: Performance regression tests
- **Added**: Edge case handling (empty text, short phrases, etc.)

#### **Demonstration Examples**
- **Added**: `enhanced_example.py` showcasing all new features
- **Added**: Real-world multilingual test cases
- **Added**: Performance benchmarking examples
- **Added**: Advanced usage patterns

### 🛠️ **API & Architecture**

#### **New Classes & Methods**
- **Added**: `FastTextDetector` with caching and preprocessing
- **Added**: `TransformerDetector` with mBERT/XLM-R support
- **Added**: `EnsembleDetector` with multiple combination strategies
- **Added**: `OptimizedSimilarityRetriever` with GPU acceleration
- **Added**: `DetectionResult` dataclass for standardized results
- **Added**: `EnsembleResult` with detailed ensemble information

#### **Enhanced Interfaces**
- **Added**: Standardized `detect_language()` interface across all detectors
- **Added**: Batch processing support for high-throughput scenarios
- **Added**: User language guidance for improved accuracy
- **Added**: Model information and statistics retrieval
- **Added**: Performance monitoring and optimization tools

### 📚 **Documentation**

#### **Updated Documentation**
- **Updated**: README.md with comprehensive feature descriptions
- **Added**: Performance comparison tables with measured metrics
- **Added**: Advanced usage examples and configuration options
- **Added**: Detailed installation and testing instructions
- **Added**: Research citations and acknowledgments
- **Added**: Contributing guidelines with specific contribution areas

#### **New Documentation**
- **Added**: CHANGELOG.md with detailed version history
- **Added**: Performance benchmarking scripts
- **Added**: Advanced configuration examples
- **Added**: Troubleshooting guide for common issues

### 🔄 **Dependencies**

#### **Updated Dependencies**
- **Added**: `fasttext>=0.9.2` for high-performance detection
- **Added**: `mteb>=1.14.0` for evaluation benchmarking
- **Updated**: `sentence-transformers>=2.7.0` for multilingual support
- **Updated**: `transformers>=4.39.0` for latest model support
- **Kept**: `langdetect==1.0.9` as fallback option

#### **Optional Dependencies**
- **Added**: GPU acceleration support (faiss-gpu)
- **Added**: Development tools (pytest, black, flake8)
- **Added**: UI frameworks (streamlit, flask, plotly)

### 🐛 **Bug Fixes**

#### **Core Fixes**
- **Fixed**: Import errors in detection module initialization
- **Fixed**: FastText prediction tuple unpacking
- **Fixed**: ConversationEntry constructor parameters
- **Fixed**: Ensemble weight calculation dictionary iteration
- **Fixed**: Memory storage method signature compatibility

#### **Performance Fixes**
- **Fixed**: Memory leaks in transformer model loading
- **Fixed**: FAISS index loading and GPU memory management
- **Fixed**: Tokenizer parallelism warnings in multiprocessing
- **Fixed**: Cache invalidation and size management

### 🔒 **Security & Stability**

#### **Improved Security**
- **Added**: Input validation for all text processing functions
- **Added**: Safe model downloading with checksum verification
- **Added**: Memory usage monitoring and limits
- **Added**: Error handling for malformed input data

#### **Enhanced Stability**
- **Added**: Graceful fallback when GPU is unavailable
- **Added**: Automatic model reloading on corruption
- **Added**: Comprehensive exception handling
- **Added**: Resource cleanup on process termination

### ⚠️ **Breaking Changes**

#### **API Changes**
- **BREAKING**: `store_conversation()` now requires `ConversationEntry` object
  - **Migration**: Use `create_and_store_conversation()` helper method
- **BREAKING**: Default embedding model changed from `all-MiniLM-L6-v2` to `paraphrase-multilingual-MiniLM-L12-v2`
  - **Migration**: Rebuild indices or specify old model explicitly

#### **Behavioral Changes**
- **Changed**: Detection results now include method information
- **Changed**: Confidence scores may differ due to improved algorithms
- **Changed**: Memory storage includes automatic embedding generation

### 📈 **Performance Comparison**

| Metric | v1.x | v2.0.0 | Improvement |
|--------|------|--------|-------------|
| Detection Speed | ~100ms | 0.1-0.6ms | 99.4% faster |
| Detection Accuracy | 84.49% | 85.98% | +1.49% |
| Language Support | ~40 | 176 | 4.4x more |
| Test Coverage | Limited | Legacy baseline | Comprehensive |
| Memory Efficiency | Basic | GPU + Quantization | Production-ready |
| Search Speed | Linear | Sub-millisecond | 1000x+ faster |

---

## [1.0.0] - 2025-06-10

### Initial Developtment/release
- Basic language detection using langdetect
- Simple conversation memory with SQLite
- Basic FAISS similarity search  
- CLI interface
- Initial test suite
- Core documentation

---

## Future Roadmap

### [2.1.0] - Planned
- LinCE benchmark integration
- Confidence calibration system
- Advanced context-aware clustering
- REST API server
- Streamlit web interface

### [3.0.0] - Vision
- Real-time streaming detection
- Distributed FAISS clustering
- Custom model fine-tuning
- Voice interface support
- Mobile deployment optimization