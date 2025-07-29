#!/usr/bin/env python3
"""
Minimal test that imports directly from text module
"""

print("Starting minimal test...")

try:
    # Import directly from the module, bypassing __init__.py
    import sys
    sys.path.insert(0, '.')
    from textregress.utils.text import chunk_text
    print("✓ Direct import successful")
    
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