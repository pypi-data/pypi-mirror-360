#!/usr/bin/env python3
"""
Quick test for chunk_text function
"""

from textregress.utils.text import chunk_text

# Test the problematic case
text = "one two three four five six seven eight nine"
print(f"Input: {text}")
print(f"Length: {len(text)}")

print("\nTesting with max_length=3, overlap=1:")
chunks = chunk_text(text, max_length=3, overlap=1)
print(f"Result: {chunks}")
print(f"Number of chunks: {len(chunks)}")

print("\nTesting with max_length=5, overlap=0:")
chunks2 = chunk_text(text, max_length=5, overlap=0)
print(f"Result: {chunks2}")
print(f"Number of chunks: {len(chunks2)}")

print("\nTesting with max_length=10, overlap=2:")
chunks3 = chunk_text(text, max_length=10, overlap=2)
print(f"Result: {chunks3}")
print(f"Number of chunks: {len(chunks3)}")

print("\n✓ All tests completed!") 