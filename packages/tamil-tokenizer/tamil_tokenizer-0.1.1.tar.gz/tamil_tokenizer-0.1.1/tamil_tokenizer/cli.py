"""
Command-line interface for tamil-tokenizer.
"""

import argparse
import sys
import json
from typing import List

from .core import TamilTokenizer, tokenize_words, tokenize_sentences, tokenize_characters
from .exceptions import InvalidTextError, TokenizationError


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Tamil text tokenization tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tamil-tokenizer "தமிழ் மொழி அழகான மொழி"           # Tokenize into words (default)
  tamil-tokenizer --method sentences "வணக்கம். நலமா?"  # Tokenize into sentences
  tamil-tokenizer --method characters "தமிழ்"         # Tokenize into characters
  tamil-tokenizer --stats "தமிழ் உரை"                # Show text statistics
  tamil-tokenizer --clean "தமிழ்   உரை"              # Clean text
        """
    )
    
    parser.add_argument(
        "text",
        help="Tamil text to tokenize"
    )
    
    parser.add_argument(
        "--method", "-m",
        choices=["words", "sentences", "characters"],
        default="words",
        help="Tokenization method (default: words)"
    )
    
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show text statistics instead of tokenizing"
    )
    
    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="Clean text instead of tokenizing"
    )
    
    parser.add_argument(
        "--remove-punctuation",
        action="store_true",
        help="Remove punctuation when cleaning text"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        tokenizer = TamilTokenizer()
        
        if args.stats:
            show_statistics(tokenizer, args.text, args.json, args.verbose)
        elif args.clean:
            clean_text_output(tokenizer, args.text, args.remove_punctuation, args.json, args.verbose)
        else:
            tokenize_text(tokenizer, args.text, args.method, args.json, args.verbose)
    
    except InvalidTextError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except TokenizationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def tokenize_text(tokenizer: TamilTokenizer, text: str, method: str, json_output: bool, verbose: bool) -> None:
    """Tokenize text using the specified method."""
    try:
        tokens = tokenizer.tokenize(text, method)
        
        if json_output:
            result = {
                "method": method,
                "input_text": text,
                "tokens": tokens,
                "token_count": len(tokens)
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if verbose:
                print(f"Tokenization method: {method}")
                print(f"Input text: {text}")
                print(f"Token count: {len(tokens)}")
                print("Tokens:")
                print("-" * 20)
            
            for i, token in enumerate(tokens, 1):
                if verbose:
                    print(f"{i:3d}. {token}")
                else:
                    print(token)
    
    except Exception as e:
        raise TokenizationError(f"Failed to tokenize text: {str(e)}")


def show_statistics(tokenizer: TamilTokenizer, text: str, json_output: bool, verbose: bool) -> None:
    """Show text statistics."""
    try:
        stats = tokenizer.get_statistics(text)
        
        if json_output:
            result = {
                "input_text": text,
                "statistics": stats
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if verbose:
                print(f"Input text: {text}")
                print("Statistics:")
                print("-" * 20)
            
            print(f"Total characters: {stats['total_characters']}")
            print(f"Tamil characters: {stats['tamil_characters']}")
            print(f"Words: {stats['words']}")
            print(f"Sentences: {stats['sentences']}")
            print(f"Average word length: {stats['average_word_length']:.2f}")
            print(f"Average sentence length: {stats['average_sentence_length']:.2f}")
    
    except Exception as e:
        raise TokenizationError(f"Failed to get statistics: {str(e)}")


def clean_text_output(tokenizer: TamilTokenizer, text: str, remove_punctuation: bool, json_output: bool, verbose: bool) -> None:
    """Clean text and show output."""
    try:
        cleaned_text = tokenizer.clean_text(text, remove_punctuation)
        
        if json_output:
            result = {
                "input_text": text,
                "cleaned_text": cleaned_text,
                "remove_punctuation": remove_punctuation
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if verbose:
                print(f"Input text: {text}")
                print(f"Remove punctuation: {remove_punctuation}")
                print("Cleaned text:")
                print("-" * 20)
            
            print(cleaned_text)
    
    except Exception as e:
        raise TokenizationError(f"Failed to clean text: {str(e)}")


if __name__ == "__main__":
    main()
