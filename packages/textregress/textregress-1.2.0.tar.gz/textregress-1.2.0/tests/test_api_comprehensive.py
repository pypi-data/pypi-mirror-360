#!/usr/bin/env python3
"""
Comprehensive API test for textregress package.

This script tests all major features and components to ensure they work correctly.
"""

import pandas as pd
import numpy as np
import torch
import tempfile
import os
import sys

# Add the package to path
sys.path.insert(0, '.')

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test main package imports
        import textregress
        from textregress import (
            TextRegressor,
            BaseTextRegressionModel,
            register_model,
            get_model,
            list_available_models,
            BaseEncoder,
            register_encoder,
            get_encoder,
            list_available_encoders,
            BaseLoss,
            register_loss,
            get_loss_function,
            list_available_losses,
            chunk_text,
            pad_chunks,
            TextRegressionDataset,
            collate_fn,
            get_gradient_importance,
            get_attention_weights,
            integrated_gradients
        )
        print("✓ All main imports successful")
        
        # Test submodule imports
        from textregress.models import LSTMTextRegressionModel, GRUTextRegressionModel
        from textregress.encoders import SentenceTransformerEncoder
        from textregress.losses import MAELoss, MSELoss, RMSELoss
        print("✓ All submodule imports successful")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_registry_functions():
    """Test registry functions work correctly."""
    print("\nTesting registry functions...")
    
    try:
        # Test model registry
        models = list_available_models()
        print(f"✓ Available models: {models}")
        assert "lstm" in models, "LSTM model not found"
        assert "gru" in models, "GRU model not found"
        
        # Test encoder registry
        encoders = list_available_encoders()
        print(f"✓ Available encoders: {encoders}")
        assert "sentence-transformers/all-MiniLM-L6-v2" in encoders, "SentenceTransformer encoder not found"
        
        # Test loss registry
        losses = list_available_losses()
        print(f"✓ Available losses: {losses}")
        assert "mae" in losses, "MAE loss not found"
        assert "mse" in losses, "MSE loss not found"
        
        # Test getting components
        lstm_model = get_model("lstm")
        encoder = get_encoder("sentence-transformers/all-MiniLM-L6-v2")
        loss_fn = get_loss_function("mae")
        
        print("✓ All registry functions work correctly")
        return True
    except Exception as e:
        print(f"✗ Registry error: {e}")
        return False

def test_utility_functions():
    """Test utility functions work correctly."""
    print("\nTesting utility functions...")
    
    try:
        # Test text chunking
        text = "This is a test text that should be chunked into smaller pieces."
        chunks = chunk_text(text, max_length=10, overlap=2)
        print(f"✓ Text chunking: {len(chunks)} chunks created")
        assert len(chunks) > 0, "No chunks created"
        
        # Test padding
        padded_chunks = pad_chunks(chunks, max_length=15, pad_token=" ")
        print(f"✓ Padding: {len(padded_chunks)} padded chunks")
        assert all(len(chunk) == 15 for chunk in padded_chunks), "Padding not working"
        
        # Test dataset creation
        encoded_sequences = [[torch.randn(5, 384) for _ in range(3)] for _ in range(10)]
        targets = [float(i) for i in range(10)]
        dataset = TextRegressionDataset(encoded_sequences, targets)
        print(f"✓ Dataset creation: {len(dataset)} samples")
        assert len(dataset) == 10, "Dataset size incorrect"
        
        # Test collate function
        batch = [dataset[i] for i in range(3)]
        collated = collate_fn(batch)
        print(f"✓ Collate function: {collated.keys()}")
        assert "x" in collated and "y" in collated, "Collate missing keys"
        
        print("✓ All utility functions work correctly")
        return True
    except Exception as e:
        print(f"✗ Utility error: {e}")
        return False

def test_model_functionality():
    """Test model functionality including new methods."""
    print("\nTesting model functionality...")
    
    try:
        # Test LSTM model
        lstm_model = LSTMTextRegressionModel(
            encoder_output_dim=384,
            learning_rate=1e-3,
            loss_function="mae",
            exogenous_features=["feature1", "feature2"]
        )
        print("✓ LSTM model creation")
        
        # Test forward pass
        batch_size, seq_len, features = 4, 5, 384
        x = torch.randn(batch_size, seq_len, features)
        exogenous = torch.randn(batch_size, 2)
        output = lstm_model(x, exogenous)
        print(f"✓ LSTM forward pass: {output.shape}")
        
        # Test embedding extraction
        doc_emb = lstm_model.get_document_embedding(x, exogenous)
        seq_emb = lstm_model.get_sequence_embeddings(x)
        print(f"✓ LSTM embeddings: doc={doc_emb.shape}, seq={seq_emb.shape}")
        
        # Test explainability
        grad_importance = lstm_model.get_gradient_importance(x, exogenous)
        attn_weights = lstm_model.get_attention_weights(x, exogenous)
        print(f"✓ LSTM explainability: grad={grad_importance.keys()}, attn={attn_weights is not None}")
        
        # Test GRU model
        gru_model = GRUTextRegressionModel(
            encoder_output_dim=384,
            learning_rate=1e-3,
            loss_function="mae",
            exogenous_features=["feature1", "feature2"]
        )
        print("✓ GRU model creation")
        
        # Test GRU forward pass
        output = gru_model(x, exogenous)
        print(f"✓ GRU forward pass: {output.shape}")
        
        # Test GRU embedding extraction
        doc_emb = gru_model.get_document_embedding(x, exogenous)
        seq_emb = gru_model.get_sequence_embeddings(x)
        print(f"✓ GRU embeddings: doc={doc_emb.shape}, seq={seq_emb.shape}")
        
        print("✓ All model functionality works correctly")
        return True
    except Exception as e:
        print(f"✗ Model error: {e}")
        return False

def test_save_load_functionality():
    """Test save and load functionality."""
    print("\nTesting save/load functionality...")
    
    try:
        # Create a model
        model = LSTMTextRegressionModel(
            encoder_output_dim=384,
            learning_rate=1e-3,
            loss_function="mae"
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp_file:
            model_path = tmp_file.name
        
        try:
            # Test saving
            model.save(model_path)
            print("✓ Model saved successfully")
            
            # Test loading
            loaded_model = LSTMTextRegressionModel.load(model_path)
            print("✓ Model loaded successfully")
            
            # Test that loaded model works
            x = torch.randn(2, 3, 384)
            output_original = model(x)
            output_loaded = loaded_model(x)
            
            # Check outputs are similar (allowing for small numerical differences)
            assert torch.allclose(output_original, output_loaded, atol=1e-6), "Loaded model output differs"
            print("✓ Loaded model produces same output")
            
        finally:
            # Clean up
            if os.path.exists(model_path):
                os.unlink(model_path)
        
        print("✓ All save/load functionality works correctly")
        return True
    except Exception as e:
        print(f"✗ Save/load error: {e}")
        return False

def test_fit_predict_functionality():
    """Test fit_predict functionality."""
    print("\nTesting fit_predict functionality...")
    
    try:
        # Create sample data
        data = {
            'text': [
                "This is a positive review about the product.",
                "The quality is excellent and I recommend it.",
                "Not satisfied with the purchase.",
                "Great value for money.",
                "Disappointed with the service."
            ],
            'y': [4.5, 4.8, 2.1, 4.2, 1.9],
            'feature1': [1.0, 1.2, 0.8, 1.1, 0.9],
            'feature2': [0.5, 0.6, 0.3, 0.7, 0.4]
        }
        df = pd.DataFrame(data)
        
        # Create estimator
        estimator = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,  # Small number for quick test
            early_stop_enabled=False
        )
        
        # Test fit_predict
        predictions = estimator.fit_predict(df)
        print(f"✓ Fit_predict successful: {len(predictions)} predictions")
        assert len(predictions) == len(df), "Wrong number of predictions"
        
        print("✓ All fit_predict functionality works correctly")
        return True
    except Exception as e:
        print(f"✗ Fit_predict error: {e}")
        return False

def test_explainability_features():
    """Test explainability features."""
    print("\nTesting explainability features...")
    
    try:
        # Create a model
        model = LSTMTextRegressionModel(
            encoder_output_dim=384,
            learning_rate=1e-3,
            loss_function="mae",
            exogenous_features=["feature1", "feature2"]
        )
        
        # Create test data
        x = torch.randn(2, 3, 384)
        exogenous = torch.randn(2, 2)
        
        # Test gradient importance
        grad_importance = get_gradient_importance(model, x, exogenous)
        print(f"✓ Gradient importance: {grad_importance.keys()}")
        assert 'text_importance' in grad_importance, "Text importance missing"
        assert 'exogenous_importance' in grad_importance, "Exogenous importance missing"
        
        # Test attention weights (if cross-attention enabled)
        attn_weights = get_attention_weights(model, x, exogenous)
        print(f"✓ Attention weights: {attn_weights is not None}")
        
        # Test integrated gradients
        ig_importance = integrated_gradients(model, x, exogenous, steps=5)
        print(f"✓ Integrated gradients: {ig_importance.keys()}")
        assert 'text_importance' in ig_importance, "IG text importance missing"
        assert 'exogenous_importance' in ig_importance, "IG exogenous importance missing"
        
        print("✓ All explainability features work correctly")
        return True
    except Exception as e:
        print(f"✗ Explainability error: {e}")
        return False

def main():
    """Run all tests."""
    print("Starting comprehensive API test...\n")
    
    tests = [
        test_imports,
        test_registry_functions,
        test_utility_functions,
        test_model_functionality,
        test_save_load_functionality,
        test_fit_predict_functionality,
        test_explainability_features
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print(f"\n{'='*50}")
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 