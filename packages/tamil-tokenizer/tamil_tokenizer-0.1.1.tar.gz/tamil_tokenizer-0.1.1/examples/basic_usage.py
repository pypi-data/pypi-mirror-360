"""
Basic usage examples for tamil-tokenizer library.
"""

from tamil_tokenizer import (
    TamilTokenizer,
    tokenize_words,
    tokenize_sentences,
    tokenize_characters,
    tokenize_syllables,
    tokenize_graphemes,
    clean_text,
    normalize_text,
)


def main():
    """Demonstrate basic usage of the Tamil tokenizer."""
    
    # Sample Tamil text
    tamil_text = "தமிழ் மொழி அழகான மொழி. இது உலகின் பழமையான மொழிகளில் ஒன்று!"
    
    print("Tamil Tokenizer - Basic Usage Examples")
    print("=" * 50)
    print(f"Input text: {tamil_text}")
    print()
    
    # Using convenience functions
    print("1. Word Tokenization (using convenience function):")
    words = tokenize_words(tamil_text)
    print(f"   Words ({len(words)}): {words}")
    print()
    
    print("2. Sentence Tokenization (using convenience function):")
    sentences = tokenize_sentences(tamil_text)
    print(f"   Sentences ({len(sentences)}):")
    for i, sentence in enumerate(sentences, 1):
        print(f"      {i}. {sentence}")
    print()
    
    print("3. Character Tokenization (using convenience function):")
    characters = tokenize_characters(tamil_text)
    print(f"   Characters ({len(characters)}): {characters[:10]}...")  # Show first 10
    print()
    
    # Using TamilTokenizer class
    print("4. Using TamilTokenizer class:")
    tokenizer = TamilTokenizer()
    
    # General tokenize method
    print("   a) General tokenize method:")
    tokens_words = tokenizer.tokenize(tamil_text, "words")
    tokens_sentences = tokenizer.tokenize(tamil_text, "sentences")
    print(f"      Words: {len(tokens_words)} tokens")
    print(f"      Sentences: {len(tokens_sentences)} tokens")
    print()
    
    # Text cleaning
    messy_text = "  தமிழ்   மொழி   அழகு  "
    print("5. Text Cleaning:")
    print(f"   Original: '{messy_text}'")
    cleaned = clean_text(messy_text)
    print(f"   Cleaned: '{cleaned}'")
    print()
    
    # Text cleaning with punctuation removal
    text_with_punct = "தமிழ், மொழி! அழகு?"
    print("6. Text Cleaning with Punctuation Removal:")
    print(f"   Original: '{text_with_punct}'")
    cleaned_no_punct = tokenizer.clean_text(text_with_punct, remove_punctuation=True)
    print(f"   Cleaned (no punct): '{cleaned_no_punct}'")
    print()
    
    # Text normalization
    print("7. Text Normalization:")
    normalized = normalize_text(messy_text)
    print(f"   Normalized: '{normalized}'")
    print()
    
    # New features in v0.1.1
    print("8. Syllable Tokenization (New in v0.1.1):")
    syllables = tokenize_syllables("தமிழ்")
    print(f"   Syllables in 'தமிழ்': {syllables}")
    print()
    
    print("9. Grapheme Cluster Tokenization (New in v0.1.1):")
    graphemes = tokenize_graphemes("தமிழ்")
    print(f"   Graphemes in 'தமிழ்': {graphemes}")
    print()
    
    print("10. Word Structure Analysis (New in v0.1.1):")
    word_analysis = tokenizer.analyze_word_structure("தமிழ்")
    print(f"   Word: தமிழ்")
    print(f"   Is Tamil: {word_analysis['is_tamil']}")
    print(f"   Character count: {word_analysis['character_count']}")
    print(f"   Syllable count: {word_analysis['syllable_count']}")
    print(f"   Has conjuncts: {word_analysis['has_conjuncts']}")
    print(f"   Has vowel signs: {word_analysis['has_vowel_signs']}")
    print()
    
    # Enhanced Statistics
    print("11. Enhanced Text Statistics (Improved in v0.1.1):")
    stats = tokenizer.get_statistics(tamil_text)
    print(f"   Total characters: {stats['total_characters']}")
    print(f"   Tamil characters: {stats['tamil_characters']}")
    print(f"   Words: {stats['words']}")
    print(f"   Tamil words: {stats['tamil_words']}")
    print(f"   Sentences: {stats['sentences']}")
    print(f"   Syllables: {stats['syllables']}")
    print(f"   Average word length: {stats['average_word_length']:.2f}")
    print(f"   Average sentence length: {stats['average_sentence_length']:.2f}")
    print(f"   Average syllables per word: {stats['average_syllables_per_word']:.2f}")
    print(f"   Words with conjuncts: {stats['words_with_conjuncts']}")
    print(f"   Words with vowel signs: {stats['words_with_vowel_signs']}")
    print(f"   Conjunct percentage: {stats['conjunct_percentage']:.1f}%")
    print(f"   Vowel sign percentage: {stats['vowel_sign_percentage']:.1f}%")
    print()
    
    # Error handling example
    print("12. Error Handling:")
    try:
        tokenizer.tokenize_words("")  # This will raise an error
    except Exception as e:
        print(f"   Caught error: {type(e).__name__}: {e}")
    print()
    
    print("Examples completed successfully!")


if __name__ == "__main__":
    main()
