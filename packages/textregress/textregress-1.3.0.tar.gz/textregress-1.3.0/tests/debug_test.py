#!/usr/bin/env python3
"""
Debug script to test chunk function and TF-IDF encoder issues.
"""

import sys
import traceback

def test_chunk_function():
    """Test the chunk_text function"""
    print("Testing chunk_text function...")
    
    try:
        from textregress.utils.text import chunk_text
        
        # Test case from the test
        text = "one two three four five six seven eight nine"
        print(f"Input text: {text}")
        print("Calling chunk_text...")
        
        # This is likely where it freezes
        chunks = chunk_text(text, max_length=3, overlap=1)
        print(f"Chunks with max_length=3, overlap=1: {chunks}")
        
        return True
    except Exception as e:
        print(f"Error testing chunk function: {e}")
        traceback.print_exc()
        return False

def test_tfidf_encoder():
    """Test TF-IDF encoder separately"""
    print("\nTesting TF-IDF encoder...")
    
    try:
        from textregress.encoders import get_encoder
        
        # Create TF-IDF encoder
        print("Creating TF-IDF encoder...")
        encoder = get_encoder("tfidf")
        print("✓ TF-IDF encoder created")
        
        # Test data
        texts = ["hello world", "test sentence", "another test"]
        print(f"Fitting on texts: {texts}")
        
        # Fit the encoder
        encoder.fit(texts)
        print("✓ TF-IDF encoder fitted")
        
        # Test encoding
        test_text = "hello world"
        print(f"Encoding: {test_text}")
        vector = encoder.encode(test_text)
        print(f"✓ Encoded vector shape: {vector.shape}")
        print(f"✓ Encoded vector type: {type(vector)}")
        
        return True
    except Exception as e:
        print(f"Error testing TF-IDF encoder: {e}")
        traceback.print_exc()
        return False

def main():
    """Run debug tests"""
    print("=" * 60)
    print("Debug Tests for textregress 1.2.3")
    print("=" * 60)
    
    # Test chunk function first
    test_chunk_function()
    
    # If chunk function works, test TF-IDF
    print("\n" + "=" * 60)
    test_tfidf_encoder()

if __name__ == "__main__":
    main() 