"""
Core functionality for Tamil text tokenization and processing.
"""

import re
import unicodedata
from typing import List, Optional, Union, Dict, Tuple

from .exceptions import InvalidTextError, TokenizationError


class TamilTokenizer:
    """
    A class for Tamil text tokenization and processing.
    
    Provides functionality to tokenize Tamil text including:
    - Word tokenization with proper Tamil morphology handling
    - Sentence tokenization
    - Character tokenization with proper grapheme clustering
    - Text cleaning and normalization
    """
    
    def __init__(self) -> None:
        """Initialize the Tamil tokenizer."""
        # Tamil Unicode ranges
        # Main Tamil block: U+0B80–U+0BFF
        # Tamil Supplement: U+11FC0–U+11FFF (not commonly used)
        self.tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+')
        
        # Tamil base consonants (க-ன், ப-ஹ)
        self.tamil_consonants = re.compile(r'[\u0B95-\u0BB9]')
        
        # Tamil vowels (அ-ஔ)
        self.tamil_vowels = re.compile(r'[\u0B85-\u0B94]')
        
        # Tamil vowel signs (ா-ௌ)
        self.tamil_vowel_signs = re.compile(r'[\u0BBE-\u0BCC]')
        
        # Tamil combining marks (், ௗ)
        self.tamil_combining = re.compile(r'[\u0BCD\u0BD7]')
        
        # Common Tamil punctuation and sentence endings
        self.sentence_endings = r'[.!?।॥]'
        
        # Enhanced word pattern that handles Tamil script properly
        # This matches sequences of Tamil characters including combining marks
        self.word_pattern = re.compile(r'[\u0B80-\u0BFF]+(?:[\u0BCD\u0BD7][\u0B80-\u0BFF]*)*')
        
        # Whitespace and punctuation patterns
        self.whitespace_pattern = re.compile(r'\s+')
        self.punctuation_pattern = re.compile(r'[^\u0B80-\u0BFF\s]')
        
        # Tamil grapheme cluster pattern for proper character tokenization
        # This handles complex Tamil characters with combining marks
        self.grapheme_pattern = re.compile(
            r'[\u0B85-\u0B94]|'  # Independent vowels
            r'[\u0B95-\u0BB9](?:[\u0BCD][\u0B95-\u0BB9])*[\u0BBE-\u0BCC\u0BD7]?|'  # Consonants with optional conjuncts and vowel signs
            r'[\u0B95-\u0BB9][\u0BCD](?![\u0B95-\u0BB9])|'  # Consonant with virama (not followed by another consonant)
            r'[\u0B80-\u0BFF]'  # Any other Tamil character
        )
    
    def _validate_text(self, text: Union[str, None]) -> str:
        """
        Validate input text.
        
        Args:
            text: Input text to validate
            
        Returns:
            Validated text as string
            
        Raises:
            InvalidTextError: If text is invalid
        """
        if text is None:
            raise InvalidTextError("Text cannot be None")
        
        if not isinstance(text, str):
            raise InvalidTextError("Text must be a string")
        
        if not text.strip():
            raise InvalidTextError("Text cannot be empty or only whitespace")
        
        return text.strip()
    
    def tokenize_words(self, text: str) -> List[str]:
        """
        Tokenize Tamil text into words.
        
        Args:
            text: Tamil text to tokenize
            
        Returns:
            List of word tokens
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If tokenization fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Find all Tamil word sequences
            words = self.word_pattern.findall(validated_text)
            
            # Clean up words by removing extra whitespace
            cleaned_words = []
            for word in words:
                cleaned_word = re.sub(r'\s+', ' ', word.strip())
                if cleaned_word:
                    cleaned_words.append(cleaned_word)
            
            return cleaned_words
            
        except Exception as e:
            if isinstance(e, (InvalidTextError, TokenizationError)):
                raise
            raise TokenizationError(f"Failed to tokenize words: {str(e)}")
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenize Tamil text into sentences.
        
        Args:
            text: Tamil text to tokenize
            
        Returns:
            List of sentence tokens
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If tokenization fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Split by sentence endings
            sentences = re.split(self.sentence_endings, validated_text)
            
            # Clean up sentences
            cleaned_sentences = []
            for sentence in sentences:
                cleaned_sentence = sentence.strip()
                if cleaned_sentence:
                    cleaned_sentences.append(cleaned_sentence)
            
            return cleaned_sentences
            
        except Exception as e:
            if isinstance(e, (InvalidTextError, TokenizationError)):
                raise
            raise TokenizationError(f"Failed to tokenize sentences: {str(e)}")
    
    def tokenize_characters(self, text: str) -> List[str]:
        """
        Tokenize Tamil text into individual Unicode characters.
        
        This method returns individual Tamil Unicode characters,
        including base characters, vowel signs, and combining marks separately.
        
        Args:
            text: Tamil text to tokenize
            
        Returns:
            List of individual Tamil Unicode characters (excluding whitespace)
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If tokenization fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Extract individual Tamil characters
            characters = []
            for char in validated_text:
                if self.tamil_pattern.match(char):
                    characters.append(char)
            
            return characters
            
        except Exception as e:
            if isinstance(e, (InvalidTextError, TokenizationError)):
                raise
            raise TokenizationError(f"Failed to tokenize characters: {str(e)}")
    
    def tokenize_graphemes(self, text: str) -> List[str]:
        """
        Tokenize Tamil text into grapheme clusters (logical characters).
        
        This method properly handles Tamil script's complex character structure,
        including base characters with combining marks, conjunct consonants, etc.
        
        Args:
            text: Tamil text to tokenize
            
        Returns:
            List of grapheme cluster tokens (excluding whitespace)
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If tokenization fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Use grapheme pattern to extract proper Tamil character clusters
            graphemes = self.grapheme_pattern.findall(validated_text)
            
            # Filter out empty matches and non-Tamil characters
            filtered_graphemes = []
            for grapheme in graphemes:
                if grapheme and self.tamil_pattern.match(grapheme):
                    filtered_graphemes.append(grapheme)
            
            return filtered_graphemes
            
        except Exception as e:
            if isinstance(e, (InvalidTextError, TokenizationError)):
                raise
            raise TokenizationError(f"Failed to tokenize graphemes: {str(e)}")
    
    def clean_text(self, text: str, remove_punctuation: bool = False) -> str:
        """
        Clean Tamil text by normalizing whitespace and optionally removing punctuation.
        
        Args:
            text: Text to clean
            remove_punctuation: Whether to remove non-Tamil punctuation
            
        Returns:
            Cleaned text
            
        Raises:
            InvalidTextError: If text is invalid
        """
        try:
            validated_text = self._validate_text(text)
            
            # Normalize whitespace
            cleaned_text = self.whitespace_pattern.sub(' ', validated_text)
            
            # Remove punctuation if requested
            if remove_punctuation:
                cleaned_text = self.punctuation_pattern.sub('', cleaned_text)
            
            return cleaned_text.strip()
            
        except Exception as e:
            if isinstance(e, InvalidTextError):
                raise
            raise TokenizationError(f"Failed to clean text: {str(e)}")
    
    def normalize_text(self, text: str, form: str = "NFC", 
                      standardize_digits: bool = True,
                      standardize_punctuation: bool = True,
                      remove_zero_width: bool = True) -> str:
        """
        Comprehensive Tamil text normalization.
        
        Args:
            text: Text to normalize
            form: Unicode normalization form ("NFC", "NFD", "NFKC", "NFKD")
            standardize_digits: Whether to standardize Tamil/Arabic numerals
            standardize_punctuation: Whether to standardize punctuation marks
            remove_zero_width: Whether to remove zero-width characters
            
        Returns:
            Normalized text
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If normalization fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Step 1: Unicode normalization
            from typing import Literal
            valid_forms: List[Literal['NFC', 'NFD', 'NFKC', 'NFKD']] = ['NFC', 'NFD', 'NFKC', 'NFKD']
            if form.upper() in valid_forms:
                normalized_text = unicodedata.normalize(form.upper(), validated_text)  # type: ignore
            else:
                normalized_text = unicodedata.normalize('NFC', validated_text)
            
            # Step 2: Remove zero-width characters if requested
            if remove_zero_width:
                # Remove zero-width joiner, non-joiner, and other invisible characters
                zero_width_chars = ['\u200C', '\u200D', '\u200B', '\uFEFF', '\u00AD']
                for char in zero_width_chars:
                    normalized_text = normalized_text.replace(char, '')
            
            # Step 3: Standardize digits if requested
            if standardize_digits:
                normalized_text = self._standardize_digits(normalized_text)
            
            # Step 4: Standardize punctuation if requested
            if standardize_punctuation:
                normalized_text = self._standardize_punctuation(normalized_text)
            
            # Step 5: Clean whitespace
            normalized_text = self.clean_text(normalized_text)
            
            return normalized_text
            
        except Exception as e:
            if isinstance(e, InvalidTextError):
                raise
            raise TokenizationError(f"Failed to normalize text: {str(e)}")
    
    def _standardize_digits(self, text: str) -> str:
        """
        Standardize Tamil and Arabic numerals.
        
        Args:
            text: Text containing digits
            
        Returns:
            Text with standardized digits
        """
        # Tamil numerals to Arabic numerals mapping
        tamil_to_arabic = {
            '௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4',
            '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9'
        }
        
        # Replace Tamil numerals with Arabic numerals
        for tamil_digit, arabic_digit in tamil_to_arabic.items():
            text = text.replace(tamil_digit, arabic_digit)
        
        return text
    
    def _standardize_punctuation(self, text: str) -> str:
        """
        Standardize punctuation marks.
        
        Args:
            text: Text containing punctuation
            
        Returns:
            Text with standardized punctuation
        """
        # Common punctuation standardizations
        punctuation_map = {
            # Various quote marks to standard quotes
            '"': '"', '"': '"', ''': "'", ''': "'",
            # Various dashes to standard dash
            '–': '-', '—': '-', '―': '-',
            # Various ellipsis to standard
            '…': '...',
            # Tamil punctuation standardization
            '।': '.', '॥': '.',
        }
        
        for old_punct, new_punct in punctuation_map.items():
            text = text.replace(old_punct, new_punct)
        
        return text
    
    def tokenize(self, text: str, method: str = "words") -> List[str]:
        """
        General tokenization method.
        
        Args:
            text: Text to tokenize
            method: Tokenization method ("words", "sentences", "characters", "syllables", "graphemes")
            
        Returns:
            List of tokens based on the specified method
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If tokenization fails
        """
        method = method.lower()
        
        if method == "words":
            return self.tokenize_words(text)
        elif method == "sentences":
            return self.tokenize_sentences(text)
        elif method == "characters":
            return self.tokenize_characters(text)
        elif method == "syllables":
            return self.tokenize_syllables(text)
        elif method == "graphemes":
            return self.tokenize_graphemes(text)
        else:
            raise TokenizationError(f"Unknown tokenization method: {method}")
    
    def tokenize_syllables(self, text: str) -> List[str]:
        """
        Tokenize Tamil text into syllables.
        
        Tamil syllables follow specific patterns:
        - V (vowel)
        - CV (consonant + vowel)
        - CCV (consonant + consonant + vowel)
        
        Args:
            text: Tamil text to tokenize
            
        Returns:
            List of syllable tokens
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If tokenization fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Pattern for Tamil syllables
            syllable_pattern = re.compile(
                r'[\u0B85-\u0B94]|'  # Independent vowels (V)
                r'[\u0B95-\u0BB9](?:[\u0BCD][\u0B95-\u0BB9])*(?:[\u0BBE-\u0BCC]|[\u0BD7])?|'  # Consonant clusters with vowel signs (C+V, CC+V)
                r'[\u0B95-\u0BB9][\u0BCD](?![\u0B95-\u0BB9])'  # Consonant with virama at end
            )
            
            syllables = syllable_pattern.findall(validated_text)
            
            # Filter out empty matches
            filtered_syllables = [syl for syl in syllables if syl and self.tamil_pattern.match(syl)]
            
            return filtered_syllables
            
        except Exception as e:
            if isinstance(e, (InvalidTextError, TokenizationError)):
                raise
            raise TokenizationError(f"Failed to tokenize syllables: {str(e)}")
    
    def analyze_word_structure(self, word: str) -> dict:
        """
        Analyze the structure of a Tamil word.
        
        Args:
            word: Tamil word to analyze
            
        Returns:
            Dictionary containing word structure analysis
        """
        try:
            if not word or not self.tamil_pattern.match(word):
                return {
                    'is_tamil': False,
                    'characters': [],
                    'syllables': [],
                    'character_count': 0,
                    'syllable_count': 0,
                    'has_conjuncts': False,
                    'has_vowel_signs': False
                }
            
            characters = self.tokenize_characters(word)
            syllables = self.tokenize_syllables(word)
            
            # Check for conjuncts (consonant clusters)
            has_conjuncts = bool(re.search(r'[\u0B95-\u0BB9][\u0BCD][\u0B95-\u0BB9]', word))
            
            # Check for vowel signs
            has_vowel_signs = bool(re.search(r'[\u0BBE-\u0BCC\u0BD7]', word))
            
            return {
                'is_tamil': True,
                'characters': characters,
                'syllables': syllables,
                'character_count': len(characters),
                'syllable_count': len(syllables),
                'has_conjuncts': has_conjuncts,
                'has_vowel_signs': has_vowel_signs
            }
            
        except Exception as e:
            raise TokenizationError(f"Failed to analyze word structure: {str(e)}")
    
    def get_statistics(self, text: str) -> dict:
        """
        Get comprehensive statistics about Tamil text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing text statistics
        """
        try:
            validated_text = self._validate_text(text)
            
            words = self.tokenize_words(validated_text)
            sentences = self.tokenize_sentences(validated_text)
            characters = self.tokenize_characters(validated_text)
            syllables = self.tokenize_syllables(validated_text)
            
            # Analyze word structures
            word_structures = [self.analyze_word_structure(word) for word in words]
            tamil_words = [ws for ws in word_structures if ws['is_tamil']]
            
            # Count conjuncts and vowel signs
            words_with_conjuncts = sum(1 for ws in tamil_words if ws['has_conjuncts'])
            words_with_vowel_signs = sum(1 for ws in tamil_words if ws['has_vowel_signs'])
            
            return {
                'total_characters': len(validated_text),
                'tamil_characters': len(characters),
                'words': len(words),
                'tamil_words': len(tamil_words),
                'sentences': len(sentences),
                'syllables': len(syllables),
                'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
                'average_sentence_length': len(words) / len(sentences) if sentences else 0,
                'average_syllables_per_word': len(syllables) / len(words) if words else 0,
                'words_with_conjuncts': words_with_conjuncts,
                'words_with_vowel_signs': words_with_vowel_signs,
                'conjunct_percentage': (words_with_conjuncts / len(tamil_words) * 100) if tamil_words else 0,
                'vowel_sign_percentage': (words_with_vowel_signs / len(tamil_words) * 100) if tamil_words else 0,
            }
            
        except Exception as e:
            if isinstance(e, InvalidTextError):
                raise
            raise TokenizationError(f"Failed to get statistics: {str(e)}")
    
    def get_script_info(self, text: str) -> Dict[str, Union[int, float, bool, List[str], Dict[str, int]]]:
        """
        Get comprehensive script information about the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing script information
            
        Raises:
            InvalidTextError: If text is invalid
            TokenizationError: If analysis fails
        """
        try:
            validated_text = self._validate_text(text)
            
            # Basic character analysis
            total_chars = len(validated_text)
            tamil_chars = len(self.tokenize_characters(validated_text))
            
            # Script detection
            scripts: Dict[str, int] = self._detect_scripts(validated_text)
            is_mixed_script = len(scripts) > 1
            is_primarily_tamil = scripts.get('Tamil', 0) > (total_chars * 0.5)
            
            # Tamil-specific analysis
            vowel_count = len(self.tamil_vowels.findall(validated_text))
            consonant_count = len(self.tamil_consonants.findall(validated_text))
            vowel_sign_count = len(self.tamil_vowel_signs.findall(validated_text))
            combining_mark_count = len(self.tamil_combining.findall(validated_text))
            
            # Character type distribution
            char_types = self._analyze_character_types(validated_text)
            
            # Complexity metrics
            complexity_score = self._calculate_complexity_score(validated_text)
            
            result: Dict[str, Union[int, float, bool, List[str], Dict[str, int]]] = {
                'total_characters': total_chars,
                'tamil_characters': tamil_chars,
                'tamil_percentage': (tamil_chars / total_chars * 100) if total_chars > 0 else 0,
                'scripts_detected': scripts,
                'is_mixed_script': is_mixed_script,
                'is_primarily_tamil': is_primarily_tamil,
                'vowel_count': vowel_count,
                'consonant_count': consonant_count,
                'vowel_sign_count': vowel_sign_count,
                'combining_mark_count': combining_mark_count,
                'character_types': char_types,
                'complexity_score': complexity_score,
                'unicode_blocks': self._identify_unicode_blocks(validated_text),
                'has_conjuncts': bool(re.search(r'[\u0B95-\u0BB9][\u0BCD][\u0B95-\u0BB9]', validated_text)),
                'has_tamil_numerals': bool(re.search(r'[௦-௯]', validated_text)),
                'has_mixed_numerals': self._has_mixed_numerals(validated_text),
            }
            # Add readability_level separately to avoid type issues
            result['readability_level'] = self._assess_readability_level(complexity_score)  # type: ignore
            return result
            
        except Exception as e:
            if isinstance(e, InvalidTextError):
                raise
            raise TokenizationError(f"Failed to get script info: {str(e)}")
    
    def _detect_scripts(self, text: str) -> Dict[str, int]:
        """
        Detect different scripts in the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping script names to character counts
        """
        scripts: Dict[str, int] = {}
        
        for char in text:
            if char.isspace():
                continue
                
            # Get Unicode script name
            try:
                script_name = unicodedata.name(char, '').split()[0]
                if 'TAMIL' in unicodedata.name(char, ''):
                    script_name = 'Tamil'
                elif char.isascii() and char.isalpha():
                    script_name = 'Latin'
                elif char.isdigit():
                    script_name = 'Digit'
                elif not char.isalnum():
                    script_name = 'Punctuation'
                else:
                    # Try to determine script from Unicode block
                    code_point = ord(char)
                    if 0x0B80 <= code_point <= 0x0BFF:
                        script_name = 'Tamil'
                    elif 0x0000 <= code_point <= 0x007F:
                        script_name = 'Latin'
                    elif 0x0900 <= code_point <= 0x097F:
                        script_name = 'Devanagari'
                    else:
                        script_name = 'Other'
                        
                scripts[script_name] = scripts.get(script_name, 0) + 1
                
            except Exception:
                scripts['Unknown'] = scripts.get('Unknown', 0) + 1
        
        return scripts
    
    def _analyze_character_types(self, text: str) -> Dict[str, int]:
        """
        Analyze different types of characters in the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping character types to counts
        """
        char_types = {
            'vowels': 0,
            'consonants': 0,
            'vowel_signs': 0,
            'combining_marks': 0,
            'digits': 0,
            'punctuation': 0,
            'whitespace': 0,
            'other': 0
        }
        
        for char in text:
            if char.isspace():
                char_types['whitespace'] += 1
            elif self.tamil_vowels.match(char):
                char_types['vowels'] += 1
            elif self.tamil_consonants.match(char):
                char_types['consonants'] += 1
            elif self.tamil_vowel_signs.match(char):
                char_types['vowel_signs'] += 1
            elif self.tamil_combining.match(char):
                char_types['combining_marks'] += 1
            elif char.isdigit() or re.match(r'[௦-௯]', char):
                char_types['digits'] += 1
            elif not char.isalnum():
                char_types['punctuation'] += 1
            else:
                char_types['other'] += 1
        
        return char_types
    
    def _calculate_complexity_score(self, text: str) -> float:
        """
        Calculate a complexity score for the Tamil text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Complexity score (0.0 to 10.0)
        """
        if not text.strip():
            return 0.0
        
        score = 0.0
        
        # Base score from character diversity
        unique_chars = len(set(text))
        total_chars = len(text)
        if total_chars > 0:
            score += (unique_chars / total_chars) * 2
        
        # Conjunct consonants add complexity
        conjuncts = len(re.findall(r'[\u0B95-\u0BB9][\u0BCD][\u0B95-\u0BB9]', text))
        score += min(conjuncts * 0.5, 2.0)
        
        # Vowel signs add moderate complexity
        vowel_signs = len(self.tamil_vowel_signs.findall(text))
        score += min(vowel_signs * 0.2, 1.5)
        
        # Long words add complexity
        words = self.tokenize_words(text)
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
            score += min(avg_word_length * 0.1, 2.0)
        
        # Mixed scripts add complexity
        scripts = self._detect_scripts(text)
        if len(scripts) > 1:
            score += 1.0
        
        # Normalize to 0-10 scale
        return min(score, 10.0)
    
    def _assess_readability_level(self, complexity_score: float) -> str:
        """
        Assess readability level based on complexity score.
        
        Args:
            complexity_score: Complexity score (0.0 to 10.0)
            
        Returns:
            Readability level string
        """
        if complexity_score <= 2.0:
            return "Very Easy"
        elif complexity_score <= 4.0:
            return "Easy"
        elif complexity_score <= 6.0:
            return "Moderate"
        elif complexity_score <= 8.0:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _identify_unicode_blocks(self, text: str) -> List[str]:
        """
        Identify Unicode blocks present in the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of Unicode block names
        """
        blocks = set()
        
        for char in text:
            code_point = ord(char)
            
            if 0x0B80 <= code_point <= 0x0BFF:
                blocks.add("Tamil")
            elif 0x0000 <= code_point <= 0x007F:
                blocks.add("Basic Latin")
            elif 0x0080 <= code_point <= 0x00FF:
                blocks.add("Latin-1 Supplement")
            elif 0x0100 <= code_point <= 0x017F:
                blocks.add("Latin Extended-A")
            elif 0x0900 <= code_point <= 0x097F:
                blocks.add("Devanagari")
            elif 0x2000 <= code_point <= 0x206F:
                blocks.add("General Punctuation")
            elif 0x2070 <= code_point <= 0x209F:
                blocks.add("Superscripts and Subscripts")
            else:
                blocks.add("Other")
        
        return sorted(list(blocks))
    
    def _has_mixed_numerals(self, text: str) -> bool:
        """
        Check if text contains both Tamil and Arabic numerals.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text has mixed numerals
        """
        has_tamil_numerals = bool(re.search(r'[௦-௯]', text))
        has_arabic_numerals = bool(re.search(r'[0-9]', text))
        
        return has_tamil_numerals and has_arabic_numerals
    
    def detect_language(self, text: str) -> Dict[str, Union[str, float, bool]]:
        """
        Detect the primary language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing language detection results
        """
        try:
            validated_text = self._validate_text(text)
            
            script_info = self.get_script_info(validated_text)
            scripts_detected = script_info['scripts_detected']
            
            # Type assertion to ensure we have the right type
            if isinstance(scripts_detected, dict):
                scripts: Dict[str, int] = scripts_detected
            else:
                scripts = {}
            
            # Determine primary language
            if scripts.get('Tamil', 0) > 0:
                tamil_percentage_val = script_info['tamil_percentage']
                if isinstance(tamil_percentage_val, (int, float)):
                    tamil_percentage = float(tamil_percentage_val)
                else:
                    tamil_percentage = 0.0
                
                if tamil_percentage >= 80:
                    primary_language = "Tamil"
                    confidence = 0.9
                elif tamil_percentage >= 50:
                    primary_language = "Tamil (Mixed)"
                    confidence = 0.7
                else:
                    primary_language = "Mixed (Tamil minority)"
                    confidence = 0.5
            else:
                primary_language = "Non-Tamil"
                confidence = 0.9
            
            result: Dict[str, Union[str, float, bool]] = {
                'primary_language': primary_language,
                'confidence': confidence,
                'is_tamil': scripts.get('Tamil', 0) > 0,
                'is_mixed_language': len(scripts) > 1,
            }
            # Add script_distribution separately to avoid type issues
            result['script_distribution'] = scripts  # type: ignore
            return result
            
        except Exception as e:
            if isinstance(e, InvalidTextError):
                raise
            raise TokenizationError(f"Failed to detect language: {str(e)}")
    
    def is_valid_tamil_text(self, text: str, min_tamil_percentage: float = 50.0) -> bool:
        """
        Check if text is valid Tamil text based on script analysis.
        
        Args:
            text: Text to validate
            min_tamil_percentage: Minimum percentage of Tamil characters required
            
        Returns:
            True if text meets Tamil validation criteria
        """
        try:
            if not text or not text.strip():
                return False
            
            script_info = self.get_script_info(text)
            tamil_percentage_val = script_info['tamil_percentage']
            
            if isinstance(tamil_percentage_val, (int, float)):
                tamil_percentage = float(tamil_percentage_val)
            else:
                tamil_percentage = 0.0
            
            return tamil_percentage >= min_tamil_percentage
            
        except Exception:
            return False


# Global instance for convenience functions
_default_tokenizer: Optional[TamilTokenizer] = None


def _get_default_tokenizer() -> TamilTokenizer:
    """Get or create the default TamilTokenizer instance."""
    global _default_tokenizer
    if _default_tokenizer is None:
        _default_tokenizer = TamilTokenizer()
    return _default_tokenizer


# Convenience functions
def tokenize_words(text: str) -> List[str]:
    """
    Convenience function to tokenize Tamil text into words.
    
    Args:
        text: Tamil text to tokenize
        
    Returns:
        List of word tokens
    """
    return _get_default_tokenizer().tokenize_words(text)


def tokenize_sentences(text: str) -> List[str]:
    """
    Convenience function to tokenize Tamil text into sentences.
    
    Args:
        text: Tamil text to tokenize
        
    Returns:
        List of sentence tokens
    """
    return _get_default_tokenizer().tokenize_sentences(text)


def tokenize_characters(text: str) -> List[str]:
    """
    Convenience function to tokenize Tamil text into characters.
    
    Args:
        text: Tamil text to tokenize
        
    Returns:
        List of character tokens
    """
    return _get_default_tokenizer().tokenize_characters(text)


def tokenize_syllables(text: str) -> List[str]:
    """
    Convenience function to tokenize Tamil text into syllables.
    
    Args:
        text: Tamil text to tokenize
        
    Returns:
        List of syllable tokens
    """
    return _get_default_tokenizer().tokenize_syllables(text)


def tokenize_graphemes(text: str) -> List[str]:
    """
    Convenience function to tokenize Tamil text into grapheme clusters.
    
    Args:
        text: Tamil text to tokenize
        
    Returns:
        List of grapheme cluster tokens
    """
    return _get_default_tokenizer().tokenize_graphemes(text)


def clean_text(text: str, remove_punctuation: bool = False) -> str:
    """
    Convenience function to clean Tamil text.
    
    Args:
        text: Text to clean
        remove_punctuation: Whether to remove punctuation
        
    Returns:
        Cleaned text
    """
    return _get_default_tokenizer().clean_text(text, remove_punctuation)


def normalize_text(text: str, form: str = "NFC", 
                  standardize_digits: bool = True,
                  standardize_punctuation: bool = True,
                  remove_zero_width: bool = True) -> str:
    """
    Convenience function to normalize Tamil text with comprehensive options.
    
    Args:
        text: Text to normalize
        form: Unicode normalization form ("NFC", "NFD", "NFKC", "NFKD")
        standardize_digits: Whether to standardize Tamil/Arabic numerals
        standardize_punctuation: Whether to standardize punctuation marks
        remove_zero_width: Whether to remove zero-width characters
        
    Returns:
        Normalized text
    """
    return _get_default_tokenizer().normalize_text(text, form, standardize_digits, standardize_punctuation, remove_zero_width)


def get_script_info(text: str) -> Dict[str, Union[int, float, bool, List[str], Dict[str, int]]]:
    """
    Convenience function to get comprehensive script information about text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing script information
    """
    return _get_default_tokenizer().get_script_info(text)


def detect_language(text: str) -> Dict[str, Union[str, float, bool]]:
    """
    Convenience function to detect the primary language of text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary containing language detection results
    """
    return _get_default_tokenizer().detect_language(text)


def is_valid_tamil_text(text: str, min_tamil_percentage: float = 50.0) -> bool:
    """
    Convenience function to check if text is valid Tamil text.
    
    Args:
        text: Text to validate
        min_tamil_percentage: Minimum percentage of Tamil characters required
        
    Returns:
        True if text meets Tamil validation criteria
    """
    return _get_default_tokenizer().is_valid_tamil_text(text, min_tamil_percentage)
