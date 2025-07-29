"""
Tests for new Text Normalization and Script Information features.
"""

import pytest
from tamil_tokenizer import (
    TamilTokenizer,
    normalize_text,
    get_script_info,
    detect_language,
    is_valid_tamil_text,
)
from tamil_tokenizer.exceptions import (
    InvalidTextError,
    TokenizationError,
)


class TestTextNormalization:
    """Test enhanced text normalization functionality."""
    
    def test_unicode_normalization_nfc(self):
        """Test Unicode NFC normalization."""
        tokenizer = TamilTokenizer()
        # Text with combining characters
        text = "தமிழ்"
        result = tokenizer.normalize_text(text, form="NFC")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_unicode_normalization_nfd(self):
        """Test Unicode NFD normalization."""
        tokenizer = TamilTokenizer()
        text = "தமிழ்"
        result = tokenizer.normalize_text(text, form="NFD")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_standardize_digits(self):
        """Test Tamil digit standardization."""
        tokenizer = TamilTokenizer()
        text = "௧௨௩ வருடம்"
        result = tokenizer.normalize_text(text, standardize_digits=True)
        assert "123" in result
        assert "௧" not in result
    
    def test_standardize_punctuation(self):
        """Test punctuation standardization."""
        tokenizer = TamilTokenizer()
        text = "தமிழ்—மொழி…அழகு"
        result = tokenizer.normalize_text(text, standardize_punctuation=True)
        assert "—" not in result
        assert "…" not in result
        assert "-" in result or "..." in result
    
    def test_remove_zero_width_characters(self):
        """Test zero-width character removal."""
        tokenizer = TamilTokenizer()
        # Text with zero-width joiner
        text = "தமிழ்\u200Cமொழி"
        result = tokenizer.normalize_text(text, remove_zero_width=True)
        assert "\u200C" not in result
        assert "தமிழ்மொழி" in result
    
    def test_convenience_function_normalize(self):
        """Test convenience function for normalization."""
        text = "  தமிழ்   மொழி  "
        result = normalize_text(text)
        assert result == "தமிழ் மொழி"
    
    def test_comprehensive_normalization(self):
        """Test comprehensive normalization with all options."""
        tokenizer = TamilTokenizer()
        text = "  தமிழ்—௧௨௩\u200Cமொழி…  "
        result = tokenizer.normalize_text(
            text,
            form="NFC",
            standardize_digits=True,
            standardize_punctuation=True,
            remove_zero_width=True
        )
        assert result.strip() == result  # No leading/trailing whitespace
        assert "123" in result  # Tamil digits converted
        assert "\u200C" not in result  # Zero-width removed
        assert "—" not in result or "…" not in result  # Punctuation standardized


class TestScriptInformation:
    """Test script information functionality."""
    
    def test_get_script_info_tamil_text(self):
        """Test script info for Tamil text."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் மொழி அழகான மொழி"
        info = tokenizer.get_script_info(text)
        
        assert isinstance(info, dict)
        assert 'total_characters' in info
        assert 'tamil_characters' in info
        assert 'tamil_percentage' in info
        assert 'scripts_detected' in info
        assert 'is_mixed_script' in info
        assert 'is_primarily_tamil' in info
        assert 'complexity_score' in info
        assert 'readability_level' in info
        assert 'unicode_blocks' in info
        
        assert info['tamil_percentage'] > 80  # Primarily Tamil
        assert info['is_primarily_tamil'] == True
        assert 'Tamil' in info['scripts_detected']
    
    def test_get_script_info_mixed_text(self):
        """Test script info for mixed Tamil-English text."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் Tamil மொழி Language"
        info = tokenizer.get_script_info(text)
        
        assert info['is_mixed_script'] == True
        assert 'Tamil' in info['scripts_detected']
        assert 'Latin' in info['scripts_detected']
        assert info['tamil_percentage'] < 100
        assert info['tamil_percentage'] > 0
    
    def test_get_script_info_with_numerals(self):
        """Test script info with Tamil numerals."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் ௧௨௩ மொழி"
        info = tokenizer.get_script_info(text)
        
        assert info['has_tamil_numerals'] == True
        assert info['has_mixed_numerals'] == False
    
    def test_get_script_info_with_mixed_numerals(self):
        """Test script info with mixed numerals."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் ௧௨௩ மொழி 456"
        info = tokenizer.get_script_info(text)
        
        assert info['has_tamil_numerals'] == True
        assert info['has_mixed_numerals'] == True
    
    def test_get_script_info_with_conjuncts(self):
        """Test script info with conjunct consonants."""
        tokenizer = TamilTokenizer()
        text = "க்ஷ த்ர"  # Contains conjuncts
        info = tokenizer.get_script_info(text)
        
        assert info['has_conjuncts'] == True
    
    def test_complexity_score_calculation(self):
        """Test complexity score calculation."""
        tokenizer = TamilTokenizer()
        
        # Simple text should have lower complexity
        simple_text = "தமிழ் மொழி"
        simple_info = tokenizer.get_script_info(simple_text)
        
        # Complex text with conjuncts should have higher complexity
        complex_text = "க்ஷத்ரிய வம்சத்தில் பிறந்த"
        complex_info = tokenizer.get_script_info(complex_text)
        
        assert simple_info['complexity_score'] < complex_info['complexity_score']
    
    def test_readability_levels(self):
        """Test readability level assessment."""
        tokenizer = TamilTokenizer()
        
        # Test different complexity levels
        simple_text = "அம்மா"
        info = tokenizer.get_script_info(simple_text)
        assert info['readability_level'] in ["Very Easy", "Easy"]
        
        complex_text = "க்ஷத்ரிய வம்சத்தில் பிறந்த மகாராஜாக்கள்"
        info = tokenizer.get_script_info(complex_text)
        # Complex text should have higher difficulty
        assert info['readability_level'] in ["Moderate", "Difficult", "Very Difficult"]
    
    def test_unicode_blocks_identification(self):
        """Test Unicode block identification."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் Tamil 123"
        info = tokenizer.get_script_info(text)
        
        blocks = info['unicode_blocks']
        assert 'Tamil' in blocks
        assert 'Basic Latin' in blocks
    
    def test_convenience_function_script_info(self):
        """Test convenience function for script info."""
        text = "தமிழ் மொழி"
        info = get_script_info(text)
        
        assert isinstance(info, dict)
        assert 'tamil_percentage' in info
        assert info['tamil_percentage'] > 80


class TestLanguageDetection:
    """Test language detection functionality."""
    
    def test_detect_tamil_language(self):
        """Test detection of Tamil language."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் மொழி அழகான மொழி"
        result = tokenizer.detect_language(text)
        
        assert isinstance(result, dict)
        assert 'primary_language' in result
        assert 'confidence' in result
        assert 'is_tamil' in result
        assert 'is_mixed_language' in result
        assert 'script_distribution' in result
        
        assert result['primary_language'] == "Tamil"
        assert result['is_tamil'] == True
        assert result['confidence'] > 0.8
    
    def test_detect_mixed_language(self):
        """Test detection of mixed language."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் Tamil Language மொழி"
        result = tokenizer.detect_language(text)
        
        assert "Mixed" in result['primary_language'] or "Tamil" in result['primary_language']
        assert result['is_mixed_language'] == True
        assert result['is_tamil'] == True
    
    def test_detect_non_tamil_language(self):
        """Test detection of non-Tamil language."""
        tokenizer = TamilTokenizer()
        text = "Hello World English Text"
        result = tokenizer.detect_language(text)
        
        assert result['primary_language'] == "Non-Tamil"
        assert result['is_tamil'] == False
        assert result['confidence'] > 0.8
    
    def test_convenience_function_detect_language(self):
        """Test convenience function for language detection."""
        text = "தமிழ் மொழி"
        result = detect_language(text)
        
        assert isinstance(result, dict)
        assert result['is_tamil'] == True


class TestTamilTextValidation:
    """Test Tamil text validation functionality."""
    
    def test_valid_tamil_text(self):
        """Test validation of valid Tamil text."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் மொழி அழகான மொழி"
        
        assert tokenizer.is_valid_tamil_text(text) == True
        assert tokenizer.is_valid_tamil_text(text, min_tamil_percentage=80.0) == True
    
    def test_mixed_text_validation(self):
        """Test validation of mixed text."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் Tamil மொழி Language"
        
        # Should pass with lower threshold
        assert tokenizer.is_valid_tamil_text(text, min_tamil_percentage=30.0) == True
        
        # Should fail with higher threshold
        assert tokenizer.is_valid_tamil_text(text, min_tamil_percentage=80.0) == False
    
    def test_non_tamil_text_validation(self):
        """Test validation of non-Tamil text."""
        tokenizer = TamilTokenizer()
        text = "Hello World English Text"
        
        assert tokenizer.is_valid_tamil_text(text) == False
    
    def test_empty_text_validation(self):
        """Test validation of empty text."""
        tokenizer = TamilTokenizer()
        
        assert tokenizer.is_valid_tamil_text("") == False
        assert tokenizer.is_valid_tamil_text("   ") == False
        assert tokenizer.is_valid_tamil_text(None) == False
    
    def test_convenience_function_validation(self):
        """Test convenience function for text validation."""
        assert is_valid_tamil_text("தமிழ் மொழி") == True
        assert is_valid_tamil_text("Hello World") == False


class TestCharacterTypeAnalysis:
    """Test character type analysis functionality."""
    
    def test_character_type_analysis(self):
        """Test analysis of different character types."""
        tokenizer = TamilTokenizer()
        text = "தமிழ் மொழி ௧௨௩ அழகு!"
        
        char_types = tokenizer._analyze_character_types(text)
        
        assert isinstance(char_types, dict)
        assert 'vowels' in char_types
        assert 'consonants' in char_types
        assert 'vowel_signs' in char_types
        assert 'combining_marks' in char_types
        assert 'digits' in char_types
        assert 'punctuation' in char_types
        assert 'whitespace' in char_types
        assert 'other' in char_types
        
        # Should have some vowels and consonants
        assert char_types['vowels'] > 0
        assert char_types['consonants'] > 0
        assert char_types['whitespace'] > 0  # Spaces between words
        assert char_types['digits'] > 0  # Tamil numerals
        assert char_types['punctuation'] > 0  # Exclamation mark


class TestErrorHandling:
    """Test error handling for new features."""
    
    def test_script_info_invalid_text(self):
        """Test script info with invalid text."""
        tokenizer = TamilTokenizer()
        
        with pytest.raises(InvalidTextError):
            tokenizer.get_script_info("")
        
        with pytest.raises(InvalidTextError):
            tokenizer.get_script_info(None)
    
    def test_language_detection_invalid_text(self):
        """Test language detection with invalid text."""
        tokenizer = TamilTokenizer()
        
        with pytest.raises(InvalidTextError):
            tokenizer.detect_language("")
        
        with pytest.raises(InvalidTextError):
            tokenizer.detect_language(None)
    
    def test_normalization_invalid_text(self):
        """Test normalization with invalid text."""
        tokenizer = TamilTokenizer()
        
        with pytest.raises(InvalidTextError):
            tokenizer.normalize_text("")
        
        with pytest.raises(InvalidTextError):
            tokenizer.normalize_text(None)


if __name__ == '__main__':
    pytest.main([__file__])
