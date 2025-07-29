# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-07

### Added
- **Enhanced Text Normalization**:
  - Comprehensive Unicode normalization (NFC, NFD, NFKC, NFKD)
  - Tamil digit standardization (௦-௯ to 0-9)
  - Punctuation standardization (quotes, dashes, ellipsis)
  - Zero-width character removal (ZWJ, ZWNJ, etc.)
  - Configurable normalization options
- **Script Information Analysis**:
  - `get_script_info()` - Comprehensive script analysis and metrics
  - `detect_language()` - Language detection with confidence scores
  - `is_valid_tamil_text()` - Tamil text validation with thresholds
  - Script detection and character distribution analysis
  - Complexity scoring and readability assessment
  - Unicode block identification
- **Character Type Analysis**:
  - Detailed character type categorization (vowels, consonants, etc.)
  - Tamil numeral detection and mixed numeral analysis
  - Conjunct consonant and vowel sign analysis
  - Character distribution statistics
- **Language Detection Features**:
  - Primary language identification
  - Mixed-language content detection
  - Confidence scoring for language predictions
  - Script distribution analysis

### Enhanced
- **TamilTokenizer Class**:
  - Enhanced `normalize_text()` with comprehensive options
  - Added `get_script_info()` for detailed script analysis
  - Added `detect_language()` for language identification
  - Added `is_valid_tamil_text()` for content validation
  - New private methods for digit/punctuation standardization
- **Convenience Functions**:
  - Enhanced `normalize_text()` with full parameter support
  - Added `get_script_info()` convenience function
  - Added `detect_language()` convenience function
  - Added `is_valid_tamil_text()` convenience function
- **Text Processing**:
  - Advanced Unicode normalization capabilities
  - Better handling of Tamil script complexities
  - Improved text quality through standardization
  - Enhanced error handling and validation

### Technical Improvements
- **Unicode Processing**:
  - Full Unicode normalization form support
  - Zero-width character handling
  - Tamil-specific character standardization
- **Analysis Algorithms**:
  - Complexity scoring based on linguistic features
  - Readability assessment with multiple levels
  - Script detection using Unicode properties
  - Character type classification system
- **Code Quality**:
  - Comprehensive test suite for new features
  - Enhanced type annotations
  - Improved error handling and validation
  - Detailed documentation and examples

### Documentation
- **New Examples**:
  - `examples/advanced_features_demo.py` - Comprehensive feature demonstration
  - Enhanced README with new feature documentation
  - Updated API reference with new methods
- **Testing**:
  - `tests/test_new_features.py` - Complete test coverage for new features
  - Enhanced test scenarios for edge cases
  - Validation tests for all new functionality

## [0.1.1] - 2025-01-07

### Added
- **Advanced Tamil Tokenization Features**:
  - `tokenize_syllables()` - Syllable-level tokenization following Tamil phonetic patterns
  - `tokenize_graphemes()` - Grapheme cluster tokenization for proper Tamil character handling
  - `analyze_word_structure()` - Detailed word structure analysis with linguistic features
- **Enhanced Character Tokenization**:
  - Improved character tokenization to handle individual Unicode characters properly
  - Fixed character tokenization test compatibility
  - Better handling of Tamil combining marks and diacritics
- **Advanced Text Analysis**:
  - Enhanced `get_statistics()` with comprehensive Tamil text metrics
  - Conjunct consonant detection and analysis
  - Vowel sign usage statistics
  - Syllable-based text analysis
- **Improved Tamil Script Support**:
  - Better handling of Tamil grapheme clusters
  - Enhanced support for consonant conjuncts (க்ஷ், ஸ்ரீ, etc.)
  - Proper vowel sign recognition and processing
  - Advanced Tamil Unicode pattern matching

### Enhanced
- **TamilTokenizer Class**:
  - Added `tokenize_syllables()` method for phonetic tokenization
  - Added `tokenize_graphemes()` method for linguistic character clustering
  - Added `analyze_word_structure()` method for morphological analysis
  - Enhanced `tokenize()` method to support "syllables" and "graphemes" methods
  - Improved `get_statistics()` with additional Tamil-specific metrics
- **Convenience Functions**:
  - Added `tokenize_syllables()` convenience function
  - Added `tokenize_graphemes()` convenience function
  - Updated module exports to include new functions
- **Regular Expression Patterns**:
  - Enhanced Tamil character pattern matching
  - Improved grapheme cluster detection
  - Better syllable boundary identification
  - Advanced consonant conjunct recognition

### Technical Improvements
- **Unicode Handling**:
  - More precise Tamil Unicode range processing (U+0B80–U+0BFF)
  - Better handling of Tamil combining characters
  - Improved vowel sign and consonant cluster detection
- **Pattern Matching**:
  - Advanced regex patterns for Tamil syllable structure
  - Enhanced grapheme cluster identification
  - Better word boundary detection for Tamil text
- **Code Quality**:
  - Maintained full type annotation coverage
  - Enhanced error handling for new features
  - Comprehensive documentation for new methods

### Fixed
- Character tokenization now returns individual Unicode characters as expected by tests
- Improved compatibility with existing test suite
- Better handling of edge cases in Tamil text processing

## [0.1.0] - 2025-01-07

### Added
- Initial release of tamil-tokenizer library
- Basic Tamil text tokenization functionality:
  - Word tokenization using Unicode Tamil character ranges
  - Sentence tokenization with Tamil punctuation support
  - Character tokenization for individual Tamil characters
- Text processing utilities:
  - Text cleaning with whitespace normalization
  - Punctuation removal options
  - Text normalization
- TamilTokenizer class with comprehensive API:
  - Object-oriented interface for all tokenization methods
  - Text statistics generation
  - Error handling with custom exceptions
- Convenience functions for quick tokenization:
  - `tokenize_words()` - Word-level tokenization
  - `tokenize_sentences()` - Sentence-level tokenization
  - `tokenize_characters()` - Character-level tokenization
  - `clean_text()` - Text cleaning utility
  - `normalize_text()` - Text normalization utility
- Command-line interface (CLI):
  - Support for all tokenization methods
  - Text statistics display
  - Text cleaning operations
  - JSON output format
  - Verbose output options
- Comprehensive test suite:
  - Unit tests for all functionality
  - Error handling tests
  - Edge case coverage
- Modern Python packaging:
  - pyproject.toml configuration
  - Type hints throughout codebase
  - Python 3.8+ support
- Documentation:
  - Comprehensive README with examples
  - API reference documentation
  - CLI usage examples
  - Development setup instructions
- Development tools configuration:
  - Black code formatting
  - MyPy type checking
  - Pytest testing framework
  - Coverage reporting

### Technical Details
- Uses regex library for efficient Tamil text processing
- Tamil Unicode range support (U+0B80–U+0BFF)
- Comprehensive error handling with custom exception classes
- Type-safe implementation with full type annotations
- Modern Python project structure following best practices

### Dependencies
- Python >= 3.8
- regex >= 2022.0.0

### Development Dependencies
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- black >= 22.0.0
- flake8 >= 5.0.0
- mypy >= 1.0.0
