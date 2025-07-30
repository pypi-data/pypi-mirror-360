#!/usr/bin/env python3
"""
Example usage of charabia-py: Python bindings for the Rust charabia tokenizer.
"""

import charabia_py

def main():
    print("=== Charabia Python Wrapper Example ===\n")
    
    # Simple tokenization using the convenience function
    print("1. Simple tokenization:")
    text = "Hello, world! This is a test with émojis 🚀 and numbers 123."
    tokens = charabia_py.tokenize(text)
    
    for token in tokens:
        print(f"  '{token.lemma}' ({token.kind}) [{token.char_start}:{token.char_end}]")
    
    print(f"\nTotal tokens: {len(tokens)}")
    
    # Using PyTokenizer for more control
    print("\n2. Using PyTokenizer:")
    tokenizer = charabia_py.PyTokenizer()
    
    # Test with different languages
    texts = [
        "The quick brown fox",
        "Café français",
        "こんにちは世界",  # Japanese
        "مرحبا بالعالم",     # Arabic
    ]
    
    for text in texts:
        print(f"\nTokenizing: '{text}'")
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            if token.is_word():
                lang = token.language if token.language else "Unknown"
                print(f"  Word: '{token.lemma}' (Script: {token.script}, Language: {lang})")
    
    # Text segmentation
    print("\n3. Text segmentation:")
    text = "Dr. Smith went to Washington, D.C. on Jan. 4th, 2023."
    segments = tokenizer.segment_str(text)
    print(f"Original: {text}")
    print(f"Segments: {segments}")
    
    # Using TokenizerBuilder for configuration
    print("\n4. Using TokenizerBuilder:")
    builder = charabia_py.PyTokenizerBuilder()
    
    # Enable lossy normalization (removes diacritics)
    builder.lossy_normalization(True)
    builder.create_char_map(True)
    
    custom_tokenizer = builder.build()
    
    # Test with accented text
    text = "Café, naïve, résumé"
    print(f"Original: {text}")
    
    tokens = custom_tokenizer.tokenize(text)
    for token in tokens:
        if token.is_word():
            print(f"  Normalized: '{token.lemma}' (original positions: {token.char_start}-{token.char_end})")

if __name__ == "__main__":
    main()
