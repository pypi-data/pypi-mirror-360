"""
Custom exceptions for the tamil-tokenizer library.
"""

from typing import Optional


class TamilTokenizerError(Exception):
    """Base exception class for tamil-tokenizer library."""
    pass


class InvalidTextError(TamilTokenizerError):
    """Raised when invalid text is provided."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class TokenizationError(TamilTokenizerError):
    """Raised when tokenization fails."""
    
    def __init__(self, message: str, text: Optional[str] = None):
        self.message = message
        self.text = text
        
        full_message = f"Tokenization failed: {message}"
        if text:
            full_message += f" (text: '{text[:50]}{'...' if len(text) > 50 else ''}')"
        
        super().__init__(full_message)
