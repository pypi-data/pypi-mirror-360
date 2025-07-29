"""
tamil-tokenizer - A simple Tamil text tokenizer library

A modern Python library for Tamil text tokenization and processing.

This library provides basic Tamil text tokenization functionality for:
- Word tokenization
- Sentence tokenization
- Character tokenization
- Basic text cleaning and normalization

Usage:
    from tamil_tokenizer import TamilTokenizer, tokenize_words, tokenize_sentences
    
    # Quick tokenization
    words = tokenize_words("தமிழ் மொழி அழகான மொழி")
    sentences = tokenize_sentences("வணக்கம். நீங்கள் எப்படி இருக்கிறீர்கள்?")
    
    # Using TamilTokenizer class
    tokenizer = TamilTokenizer()
    tokens = tokenizer.tokenize("தமிழ் உரை")
"""

from .core import (
    TamilTokenizer,
    tokenize_words,
    tokenize_sentences,
    tokenize_characters,
    tokenize_syllables,
    tokenize_graphemes,
    clean_text,
    normalize_text,
    get_script_info,
    detect_language,
    is_valid_tamil_text,
)
from .exceptions import (
    TamilTokenizerError,
    InvalidTextError,
    TokenizationError,
)

__version__ = "0.2.0"
__author__ = "Raja CSP Raman"
__email__ = "raja.csp@gmail.com"

__all__ = [
    "TamilTokenizer",
    "tokenize_words",
    "tokenize_sentences", 
    "tokenize_characters",
    "tokenize_syllables",
    "tokenize_graphemes",
    "clean_text",
    "normalize_text",
    "get_script_info",
    "detect_language",
    "is_valid_tamil_text",
    "TamilTokenizerError",
    "InvalidTextError",
    "TokenizationError",
]
