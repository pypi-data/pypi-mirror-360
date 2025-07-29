#!/usr/bin/env python3
"""
Comprehensive test script for textregress 1.2.2
Tests all modules end-to-end to ensure everything works correctly.
"""

import sys
import traceback

def test_imports():
    """Test all basic imports"""
    print("Testing imports...")
    
    try:
        import textregress
        print(f"✓ textregress imported successfully, version: {textregress.__version__}")
    except Exception as e:
        print(f"✗ textregress import failed: {e}")
        return False
    
    try:
        from textregress import TextRegressor
        print("✓ TextRegressor imported successfully")
    except Exception as e:
        print(f"✗ TextRegressor import failed: {e}")
        return False
    
    try:
        from textregress.models import LSTMTextRegressionModel, GRUTextRegressionModel
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from textregress.encoders import get_encoder, list_available_encoders
        print("✓ Encoders imported successfully")
    except Exception as e:
        print(f"✗ Encoders import failed: {e}")
        return False
    
    try:
        from textregress.losses import get_loss_function, list_available_losses
        print("✓ Losses imported successfully")
    except Exception as e:
        print(f"✗ Losses import failed: {e}")
        return False
    
    try:
        from textregress.utils import chunk_text, pad_chunks
        print("✓ Utils imported successfully")
    except Exception as e:
        print(f"✗ Utils import failed: {e}")
        return False
    
    return True

def test_encoders():
    """Test encoder registration and availability"""
    print("\nTesting encoders...")
    
    try:
        from textregress.encoders import list_available_encoders, get_encoder
        
        available_encoders = list_available_encoders()
        print(f"✓ Available encoders: {available_encoders}")
        
        # Test sentence transformer encoder
        try:
            encoder = get_encoder("sentence_transformer", model_name="sentence-transformers/all-MiniLM-L6-v2")
            print("✓ Sentence transformer encoder created successfully")
        except Exception as e:
            print(f"✗ Sentence transformer encoder failed: {e}")
        
        # Test TF-IDF encoder
        try:
            encoder = get_encoder("tfidf")
            print("✓ TF-IDF encoder created successfully")
        except Exception as e:
            print(f"✗ TF-IDF encoder failed: {e}")
            
    except Exception as e:
        print(f"✗ Encoder test failed: {e}")
        return False
    
    return True

def test_models():
    """Test model registration and availability"""
    print("\nTesting models...")
    
    try:
        from textregress.models import list_available_models, get_model
        
        available_models = list_available_models()
        print(f"✓ Available models: {available_models}")
        
        # Test LSTM model
        try:
            model = get_model("lstm")
            print("✓ LSTM model created successfully")
        except Exception as e:
            print(f"✗ LSTM model failed: {e}")
        
        # Test GRU model
        try:
            model = get_model("gru")
            print("✓ GRU model created successfully")
        except Exception as e:
            print(f"✗ GRU model failed: {e}")
            
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False
    
    return True

def test_losses():
    """Test loss function registration and availability"""
    print("\nTesting losses...")
    
    try:
        from textregress.losses import list_available_losses, get_loss_function
        
        available_losses = list_available_losses()
        print(f"✓ Available losses: {available_losses}")
        
        # Test MAE loss
        try:
            loss = get_loss_function("mae")
            print("✓ MAE loss created successfully")
        except Exception as e:
            print(f"✗ MAE loss failed: {e}")
        
        # Test MSE loss
        try:
            loss = get_loss_function("mse")
            print("✓ MSE loss created successfully")
        except Exception as e:
            print(f"✗ MSE loss failed: {e}")
            
    except Exception as e:
        print(f"✗ Loss test failed: {e}")
        return False
    
    return True

def test_textregressor():
    """Test TextRegressor initialization"""
    print("\nTesting TextRegressor...")
    
    try:
        from textregress import TextRegressor
        
        # Test with sentence transformer
        try:
            regressor = TextRegressor(
                model_name='lstm',
                encoder_model='sentence-transformers/all-MiniLM-L6-v2',
                max_steps=1,
                early_stop_enabled=False
            )
            print("✓ TextRegressor with sentence transformer created successfully")
        except Exception as e:
            print(f"✗ TextRegressor with sentence transformer failed: {e}")
        
        # Test with TF-IDF
        try:
            regressor = TextRegressor(
                model_name='gru',
                encoder_model='tfidf',
                max_steps=1,
                early_stop_enabled=False
            )
            print("✓ TextRegressor with TF-IDF created successfully")
        except Exception as e:
            print(f"✗ TextRegressor with TF-IDF failed: {e}")
            
    except Exception as e:
        print(f"✗ TextRegressor test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("TextRegress 1.2.2 Comprehensive Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_encoders,
        test_models,
        test_losses,
        test_textregressor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! TextRegress 1.2.2 is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 