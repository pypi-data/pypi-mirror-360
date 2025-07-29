#!/usr/bin/env python3
"""
Simple test to isolate the hanging issue
"""

print("Starting simple test...")

try:
    from textregress.utils.text import chunk_text
    print("✓ Import successful")
    
    text = "one two three four five six seven eight nine"
    print(f"✓ Text prepared: {text}")
    
    print("Calling chunk_text...")
    chunks = chunk_text(text, max_length=3, overlap=1)
    print(f"✓ chunk_text completed: {chunks}")
    
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc() 