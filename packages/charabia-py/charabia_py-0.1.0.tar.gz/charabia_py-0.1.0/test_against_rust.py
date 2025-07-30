#!/usr/bin/env python3
"""
Test script to compare Python wrapper output against known Rust charabia test cases.
Based on the examples in charabia/charabia/src/lib.rs and tokenizer tests.
"""

import charabia_py

def test_basic_tokenization():
    """Test based on lib.rs example: Basic tokenization with normalization"""
    print("=== Test 1: Basic Tokenization (lib.rs example) ===")
    
    # From charabia/charabia/src/lib.rs documentation
    text = "Thé quick (\"brown\") fox can't jump 32.3 feet, right? Brr, it's 29.3°F!"
    tokens = charabia_py.tokenize(text)
    
    print(f"Input: {text}")
    print("Expected first token: lemma='the' (normalized from 'Thé'), kind=word")
    print("Expected second token: lemma=' ', kind=separator")
    
    if len(tokens) > 0:
        first_token = tokens[0]
        print(f"Actual first token: lemma='{first_token.lemma}', kind={first_token.kind}, is_word={first_token.is_word()}")
        
        # Check normalization: "Thé" should become "the"
        if first_token.lemma == "the" and first_token.is_word():
            print("✅ PASS: First token correctly normalized and classified")
        else:
            print("❌ FAIL: First token normalization or classification incorrect")
    
    if len(tokens) > 1:
        second_token = tokens[1]
        print(f"Actual second token: lemma='{second_token.lemma}', kind={second_token.kind}, is_separator={second_token.is_separator()}")
        
        if second_token.lemma == " " and second_token.is_separator():
            print("✅ PASS: Second token correctly identified as separator")
        else:
            print("❌ FAIL: Second token classification incorrect")
    
    print()

def test_segmentation():
    """Test based on lib.rs example: Basic segmentation"""
    print("=== Test 2: Basic Segmentation (lib.rs example) ===")
    
    # From charabia/charabia/src/lib.rs documentation
    text = "The quick (\"brown\") fox can't jump 32.3 feet, right? Brr, it's 29.3°F!"
    tokenizer = charabia_py.PyTokenizer()
    segments = tokenizer.segment_str(text)
    
    print(f"Input: {text}")
    print("Expected first segments: ['The', ' ', 'quick', ...]")
    print(f"Actual segments (first 6): {segments[:6]}")
    
    expected_start = ["The", " ", "quick"]
    if len(segments) >= 3 and segments[:3] == expected_start:
        print("✅ PASS: Segmentation matches expected output")
    else:
        print("❌ FAIL: Segmentation doesn't match expected output")
    
    print()

def test_reconstruct_method():
    """Test the reconstruct method mentioned in tokenizer.rs"""
    print("=== Test 3: Reconstruct Method (tokenizer.rs example) ===")
    
    # From charabia/charabia/src/tokenizer.rs documentation
    text = "The quick (\"brown\") fox can't jump 32.3 feet, right? Brr, it's 29.3°F!"
    tokens = charabia_py.tokenize(text)
    
    print(f"Input: {text}")
    print("Testing position reconstruction...")
    
    # Check if we can reconstruct original text from positions
    reconstructed = ""
    for token in tokens:
        original_segment = text[token.char_start:token.char_end]
        reconstructed += original_segment
        
        print(f"Token '{token.lemma}' -> Original '{original_segment}' at {token.char_start}:{token.char_end}")
    
    if reconstructed == text:
        print("✅ PASS: Text can be perfectly reconstructed from token positions")
    else:
        print("❌ FAIL: Reconstruction failed")
        print(f"Original:      '{text}'")
        print(f"Reconstructed: '{reconstructed}'")
    
    print()

def test_multilingual():
    """Test with different languages to verify script/language detection"""
    print("=== Test 4: Multilingual Text Processing ===")
    
    test_cases = [
        ("Hello world", "Latin", None),  # English
        ("Café français", "Latin", None),  # French with accents
        ("こんにちは世界", "Cj", "Jpn"),  # Japanese
        ("مرحبا بالعالم", "Arabic", None),  # Arabic
    ]
    
    tokenizer = charabia_py.PyTokenizer()
    
    for text, expected_script, expected_language in test_cases:
        print(f"Testing: '{text}'")
        tokens = tokenizer.tokenize(text)
        
        if tokens:
            first_word = next((t for t in tokens if t.is_word()), None)
            if first_word:
                print(f"  Script: {first_word.script} (expected: {expected_script})")
                print(f"  Language: {first_word.language} (expected: {expected_language})")
                
                script_match = first_word.script == expected_script
                lang_match = (expected_language is None) or (first_word.language == expected_language)
                
                if script_match and lang_match:
                    print("  ✅ PASS: Script and language detection correct")
                else:
                    print("  ❌ FAIL: Script or language detection incorrect")
            else:
                print("  ❌ FAIL: No word tokens found")
        else:
            print("  ❌ FAIL: No tokens found")
        print()

def test_token_classification():
    """Test token classification (word, separator, etc.)"""
    print("=== Test 5: Token Classification ===")
    
    text = "Hello, world! How are you?"
    tokens = charabia_py.tokenize(text)
    
    print(f"Input: {text}")
    print("Analyzing token classification:")
    
    expected_pattern = ["word", "separator", "word", "separator", "separator", "word", "separator", "word", "separator", "word", "separator"]
    
    for i, token in enumerate(tokens[:len(expected_pattern)]):
        expected = expected_pattern[i] if i < len(expected_pattern) else "unknown"
        actual = "word" if token.is_word() else ("separator" if token.is_separator() else "other")
        
        status = "✅" if actual == expected else "❌"
        print(f"  {status} '{token.lemma}' -> {actual} (expected: {expected})")
    
    print()

def test_builder_configuration():
    """Test TokenizerBuilder configuration"""
    print("=== Test 6: TokenizerBuilder Configuration ===")
    
    text = "Café, naïve, résumé"
    print(f"Input: {text}")
    
    # Test default tokenizer
    default_tokens = charabia_py.tokenize(text)
    print("Default tokenizer:")
    for token in default_tokens:
        if token.is_word():
            print(f"  '{token.lemma}'")
    
    # Test with lossy normalization
    builder = charabia_py.PyTokenizerBuilder()
    builder.lossy_normalization(True)
    custom_tokenizer = builder.build()
    
    custom_tokens = custom_tokenizer.tokenize(text)
    print("With lossy normalization:")
    for token in custom_tokens:
        if token.is_word():
            print(f"  '{token.lemma}'")
    
    # Check if normalization worked (accents should be removed)
    word_tokens = [t.lemma for t in custom_tokens if t.is_word()]
    if "cafe" in word_tokens and "naive" in word_tokens and "resume" in word_tokens:
        print("✅ PASS: Lossy normalization working (accents removed)")
    else:
        print("❌ FAIL: Lossy normalization not working as expected")
    
    print()

def main():
    print("Testing charabia-py against known Rust charabia test cases")
    print("=" * 60)
    print()
    
    test_basic_tokenization()
    test_segmentation()
    test_reconstruct_method()
    test_multilingual()
    test_token_classification()
    test_builder_configuration()
    
    print("=" * 60)
    print("Test comparison complete!")
    print()
    print("To run the original Rust tests for comparison:")
    print("  cd charabia/charabia && cargo test")
    print("  cd charabia/charabia && cargo test tokenizer")
    print("  cd charabia/charabia && cargo test segmenter")

if __name__ == "__main__":
    main()
