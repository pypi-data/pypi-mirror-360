"""
Advanced Features Demo - Text Normalization and Script Information

This example demonstrates the enhanced text normalization and comprehensive
script information features of the tamil-tokenizer library.
"""

from tamil_tokenizer import (
    TamilTokenizer,
    normalize_text,
    get_script_info,
    detect_language,
    is_valid_tamil_text,
)


def demo_text_normalization():
    """Demonstrate comprehensive text normalization features."""
    print("=" * 60)
    print("TEXT NORMALIZATION DEMO")
    print("=" * 60)
    
    tokenizer = TamilTokenizer()
    
    # Example 1: Basic normalization
    print("\n1. Basic Text Normalization:")
    messy_text = "  தமிழ்   மொழி   அழகான   மொழி  "
    normalized = tokenizer.normalize_text(messy_text)
    print(f"Original: '{messy_text}'")
    print(f"Normalized: '{normalized}'")
    
    # Example 2: Tamil digit standardization
    print("\n2. Tamil Digit Standardization:")
    text_with_tamil_digits = "தமிழ் ௧௨௩௪ வருடங்கள் பழமையான மொழி"
    normalized_digits = tokenizer.normalize_text(text_with_tamil_digits, standardize_digits=True)
    print(f"Original: {text_with_tamil_digits}")
    print(f"Standardized: {normalized_digits}")
    
    # Example 3: Punctuation standardization
    print("\n3. Punctuation Standardization:")
    text_with_punct = "தமிழ்—மொழி…அழகான—மொழி"
    normalized_punct = tokenizer.normalize_text(text_with_punct, standardize_punctuation=True)
    print(f"Original: {text_with_punct}")
    print(f"Standardized: {normalized_punct}")
    
    # Example 4: Zero-width character removal
    print("\n4. Zero-width Character Removal:")
    text_with_zwj = "தமிழ்\u200Cமொழி\u200Dஅழகு"
    normalized_zwj = tokenizer.normalize_text(text_with_zwj, remove_zero_width=True)
    print(f"Original: {text_with_zwj} (contains invisible characters)")
    print(f"Cleaned: {normalized_zwj}")
    
    # Example 5: Comprehensive normalization
    print("\n5. Comprehensive Normalization:")
    complex_text = "  தமிழ்—௧௨௩\u200Cமொழி…அழகான—மொழி  "
    comprehensive = tokenizer.normalize_text(
        complex_text,
        form="NFC",
        standardize_digits=True,
        standardize_punctuation=True,
        remove_zero_width=True
    )
    print(f"Original: '{complex_text}'")
    print(f"Comprehensive: '{comprehensive}'")


def demo_script_information():
    """Demonstrate script information analysis features."""
    print("\n" + "=" * 60)
    print("SCRIPT INFORMATION DEMO")
    print("=" * 60)
    
    tokenizer = TamilTokenizer()
    
    # Example 1: Pure Tamil text analysis
    print("\n1. Pure Tamil Text Analysis:")
    tamil_text = "தமிழ் மொழி உலகின் பழமையான மொழிகளில் ஒன்று"
    info = tokenizer.get_script_info(tamil_text)
    
    print(f"Text: {tamil_text}")
    print(f"Total characters: {info['total_characters']}")
    print(f"Tamil characters: {info['tamil_characters']}")
    print(f"Tamil percentage: {info['tamil_percentage']:.1f}%")
    print(f"Is primarily Tamil: {info['is_primarily_tamil']}")
    print(f"Scripts detected: {info['scripts_detected']}")
    print(f"Complexity score: {info['complexity_score']:.2f}")
    print(f"Readability level: {info['readability_level']}")
    print(f"Unicode blocks: {info['unicode_blocks']}")
    
    # Example 2: Mixed script analysis
    print("\n2. Mixed Script Text Analysis:")
    mixed_text = "தமிழ் Tamil மொழி Language is beautiful"
    mixed_info = tokenizer.get_script_info(mixed_text)
    
    print(f"Text: {mixed_text}")
    print(f"Tamil percentage: {mixed_info['tamil_percentage']:.1f}%")
    print(f"Is mixed script: {mixed_info['is_mixed_script']}")
    print(f"Scripts detected: {mixed_info['scripts_detected']}")
    print(f"Unicode blocks: {mixed_info['unicode_blocks']}")
    
    # Example 3: Text with numerals and conjuncts
    print("\n3. Complex Text Analysis:")
    complex_text = "தமிழ்நாட்டில் ௧௨௩௪ வருடங்கள் முன்பு எழுதப்பட்ட நூல்கள்"
    complex_info = tokenizer.get_script_info(complex_text)
    
    print(f"Text: {complex_text}")
    print(f"Has conjuncts: {complex_info['has_conjuncts']}")
    print(f"Has Tamil numerals: {complex_info['has_tamil_numerals']}")
    print(f"Vowel count: {complex_info['vowel_count']}")
    print(f"Consonant count: {complex_info['consonant_count']}")
    print(f"Complexity score: {complex_info['complexity_score']:.2f}")
    print(f"Readability level: {complex_info['readability_level']}")
    
    # Example 4: Character type analysis
    print("\n4. Character Type Distribution:")
    char_types = complex_info['character_types']
    print("Character type breakdown:")
    for char_type, count in char_types.items():
        if count > 0:
            print(f"  {char_type.capitalize()}: {count}")


def demo_language_detection():
    """Demonstrate language detection features."""
    print("\n" + "=" * 60)
    print("LANGUAGE DETECTION DEMO")
    print("=" * 60)
    
    tokenizer = TamilTokenizer()
    
    test_texts = [
        "தமிழ் மொழி அழகான மொழி",
        "தமிழ் Tamil மொழி Language",
        "Hello World English Text",
        "தமிழ் is a beautiful language",
        "தமிழ்நாட்டின் பண்பாட்டு மரபுகள் அழகானவை"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: {text}")
        result = tokenizer.detect_language(text)
        
        print(f"   Primary language: {result['primary_language']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Is Tamil: {result['is_tamil']}")
        print(f"   Is mixed language: {result['is_mixed_language']}")
        print(f"   Script distribution: {result['script_distribution']}")


def demo_text_validation():
    """Demonstrate Tamil text validation features."""
    print("\n" + "=" * 60)
    print("TEXT VALIDATION DEMO")
    print("=" * 60)
    
    tokenizer = TamilTokenizer()
    
    test_texts = [
        ("தமிழ் மொழி அழகான மொழி", "Pure Tamil text"),
        ("தமிழ் Tamil மொழி", "Mixed Tamil-English text"),
        ("Hello World", "English text"),
        ("தமிழ் 123 English", "Multi-script text"),
        ("", "Empty text"),
    ]
    
    print("\nValidation with default threshold (50%):")
    for text, description in test_texts:
        if text:  # Skip empty text for this test
            is_valid = tokenizer.is_valid_tamil_text(text)
            print(f"  {description}: {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    print("\nValidation with strict threshold (80%):")
    for text, description in test_texts:
        if text:  # Skip empty text for this test
            is_valid = tokenizer.is_valid_tamil_text(text, min_tamil_percentage=80.0)
            print(f"  {description}: {'✓ Valid' if is_valid else '✗ Invalid'}")


def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print("\n" + "=" * 60)
    print("CONVENIENCE FUNCTIONS DEMO")
    print("=" * 60)
    
    text = "தமிழ் மொழி அழகான மொழி"
    
    print(f"\nText: {text}")
    
    # Normalization
    normalized = normalize_text(text)
    print(f"Normalized: {normalized}")
    
    # Script info
    script_info = get_script_info(text)
    print(f"Tamil percentage: {script_info['tamil_percentage']:.1f}%")
    
    # Language detection
    language = detect_language(text)
    print(f"Detected language: {language['primary_language']}")
    
    # Text validation
    is_valid = is_valid_tamil_text(text)
    print(f"Is valid Tamil text: {is_valid}")


def main():
    """Run all demos."""
    print("TAMIL TOKENIZER - ADVANCED FEATURES DEMONSTRATION")
    print("This demo showcases the enhanced text normalization and")
    print("comprehensive script information features.")
    
    try:
        demo_text_normalization()
        demo_script_information()
        demo_language_detection()
        demo_text_validation()
        demo_convenience_functions()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Please ensure the tamil-tokenizer library is properly installed.")


if __name__ == "__main__":
    main()
