#!/usr/bin/env python3
"""
Simple test to verify basic package functionality.
"""

import sys
import pandas as pd
import numpy as np

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        from textregress import TextRegressor
        print("✓ TextRegressor imported successfully")
    except Exception as e:
        print(f"✗ Failed to import TextRegressor: {e}")
        return False
    
    try:
        from textregress.models import list_available_models
        from textregress.encoders import list_available_encoders
        from textregress.losses import list_available_losses
        print("✓ Registry functions imported successfully")
    except Exception as e:
        print(f"✗ Failed to import registry functions: {e}")
        return False
    
    try:
        from textregress.utils import chunk_text, pad_chunks
        print("✓ Utility functions imported successfully")
    except Exception as e:
        print(f"✗ Failed to import utility functions: {e}")
        return False
    
    return True

def test_registry_systems():
    """Test that registry systems work correctly."""
    print("\nTesting registry systems...")
    
    try:
        from textregress.models import list_available_models
        models = list_available_models()
        print(f"✓ Available models: {models}")
        assert "lstm" in models, "LSTM model not found"
        assert "gru" in models, "GRU model not found"
    except Exception as e:
        print(f"✗ Model registry failed: {e}")
        return False
    
    try:
        from textregress.encoders import list_available_encoders
        encoders = list_available_encoders()
        print(f"✓ Available encoders: {encoders}")
        assert "sentence_transformer" in encoders, "SentenceTransformer encoder not found"
        assert "tfidf" in encoders, "TF-IDF encoder not found"
    except Exception as e:
        print(f"✗ Encoder registry failed: {e}")
        return False
    
    try:
        from textregress.losses import list_available_losses
        losses = list_available_losses()
        print(f"✓ Available losses: {losses}")
        assert "mae" in losses, "MAE loss not found"
        assert "mse" in losses, "MSE loss not found"
    except Exception as e:
        print(f"✗ Loss registry failed: {e}")
        return False
    
    return True

def test_text_processing():
    """Test text processing utilities."""
    print("\nTesting text processing utilities...")
    
    try:
        from textregress.utils import chunk_text, pad_chunks
        
        # Test chunking
        text = "This is a test text with multiple words to test the chunking functionality"
        chunks = chunk_text(text, max_length=5, overlap=2)
        print(f"✓ Text chunking: {len(chunks)} chunks created")
        assert len(chunks) > 0, "No chunks created"
        
        # Test padding
        padded_chunks = pad_chunks(chunks, padding_value=0)
        print(f"✓ Text padding: {len(padded_chunks)} chunks padded")
        
    except Exception as e:
        print(f"✗ Text processing failed: {e}")
        return False
    
    return True

def test_basic_regressor():
    """Test basic TextRegressor instantiation."""
    print("\nTesting basic TextRegressor...")
    
    try:
        from textregress import TextRegressor
        
        # Test basic instantiation
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=5
        )
        print("✓ TextRegressor instantiated successfully")
        
        # Test with different model
        regressor2 = TextRegressor(
            model_name="gru",
            encoder_model="tfidf",
            max_steps=5
        )
        print("✓ GRU + TF-IDF TextRegressor instantiated successfully")
        
    except Exception as e:
        print(f"✗ TextRegressor instantiation failed: {e}")
        return False
    
    return True

def test_simple_fit_predict():
    """Test simple fit and predict with minimal data."""
    print("\nTesting simple fit and predict...")
    
    try:
        from textregress import TextRegressor
        
        # Create minimal test data
        data = {
            'text': [
                "This is a positive review.",
                "The quality is excellent.",
                "Not satisfied with the purchase.",
                "Great value for money."
            ],
            'y': [4.5, 4.8, 2.1, 4.2]
        }
        df = pd.DataFrame(data)
        
        # Create and train model
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=5,
            learning_rate=0.001,
            batch_size=2
        )
        
        # Fit and predict
        predictions = regressor.fit_predict(df)
        print(f"✓ Fit and predict completed: {len(predictions)} predictions made")
        assert len(predictions) == len(df), "Number of predictions doesn't match data size"
        
    except Exception as e:
        print(f"✗ Simple fit and predict failed: {e}")
        return False
    
    return True

def main():
    """Run all simple tests."""
    print("Starting simple end-to-end test for textregress package...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_registry_systems,
        test_text_processing,
        test_basic_regressor,
        test_simple_fit_predict
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Package is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 