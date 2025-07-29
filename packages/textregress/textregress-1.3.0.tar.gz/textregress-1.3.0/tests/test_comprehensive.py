#!/usr/bin/env python3
"""
Comprehensive end-to-end test for textregress package.

This script tests all major functionality including:
- Different encoders (SentenceTransformer, TF-IDF)
- Different models (LSTM, GRU)
- Different loss functions
- Exogenous features
- Cross-attention
- Feature mixing
- Model persistence
- Text chunking
"""

import pandas as pd
import numpy as np
import torch
import tempfile
import os
from textregress import TextRegressor
from textregress.models import list_available_models
from textregress.encoders import list_available_encoders
from textregress.losses import list_available_losses

def create_test_data(n_samples=50):
    """Create test data with varying text lengths and exogenous features."""
    np.random.seed(42)
    
    # Create texts of varying lengths
    short_texts = [
        "This is a short text.",
        "Another brief sentence.",
        "Quick test message."
    ]
    
    medium_texts = [
        "This is a medium length text that contains more words and should be processed properly by the text regression model. It includes various topics and concepts.",
        "Another medium length document with different content and structure. This text should be long enough to test chunking functionality if needed.",
        "A third medium length text that provides additional variety to the dataset. It contains different vocabulary and sentence structures."
    ]
    
    long_texts = [
        "This is a much longer text that contains many more words and sentences. It is designed to test the chunking functionality of the text regression package. The text includes various topics, concepts, and vocabulary that should be processed by the encoder. This document should be long enough to require chunking when using appropriate chunk sizes. The content covers multiple aspects and provides a comprehensive test of the system's capabilities.",
        "Another long document with extensive content and detailed information. This text is structured to challenge the model's ability to handle large amounts of textual data. It includes complex sentences, technical terminology, and varied linguistic patterns. The length of this document ensures that chunking mechanisms are properly tested and validated. Multiple paragraphs and sections provide diverse content for thorough evaluation.",
        "A third long text document that complements the other samples with different writing styles and subject matter. This comprehensive text includes various linguistic elements such as descriptive passages, technical explanations, and narrative content. The document's length and complexity make it an ideal candidate for testing advanced features like cross-attention and feature mixing. Multiple themes and topics are explored throughout the text."
    ]
    
    # Combine all text types
    all_texts = short_texts + medium_texts + long_texts
    texts = np.random.choice(all_texts, n_samples, replace=True)
    
    # Create target values (somewhat correlated with text length)
    targets = []
    for text in texts:
        base_score = len(text.split()) / 10  # Base score from text length
        noise = np.random.normal(0, 0.5)  # Add some noise
        target = max(0, min(5, base_score + noise))  # Clamp between 0 and 5
        targets.append(target)
    
    # Create exogenous features
    feature1 = np.random.normal(1.0, 0.3, n_samples)
    feature2 = np.random.normal(0.5, 0.2, n_samples)
    feature3 = np.random.uniform(0, 1, n_samples)
    
    data = {
        'text': texts,
        'y': targets,
        'feature1': feature1,
        'feature2': feature2,
        'feature3': feature3
    }
    
    return pd.DataFrame(data)

def test_basic_functionality():
    """Test basic functionality with different configurations."""
    print("=== Testing Basic Functionality ===")
    
    # Create test data
    df = create_test_data(20)
    print(f"Created test dataset with {len(df)} samples")
    
    # Test 1: Basic LSTM with SentenceTransformer
    print("\n1. Testing LSTM + SentenceTransformer...")
    try:
        regressor1 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions1 = regressor1.fit_predict(df)
        print(f"✓ LSTM + SentenceTransformer: {len(predictions1)} predictions made")
    except Exception as e:
        print(f"✗ LSTM + SentenceTransformer failed: {e}")
    
    # Test 2: Basic GRU with SentenceTransformer
    print("\n2. Testing GRU + SentenceTransformer...")
    try:
        regressor2 = TextRegressor(
            model_name="gru",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions2 = regressor2.fit_predict(df)
        print(f"✓ GRU + SentenceTransformer: {len(predictions2)} predictions made")
    except Exception as e:
        print(f"✗ GRU + SentenceTransformer failed: {e}")
    
    # Test 3: TF-IDF encoder
    print("\n3. Testing TF-IDF encoder...")
    try:
        regressor3 = TextRegressor(
            model_name="lstm",
            encoder_model="tfidf",
            encoder_params={"max_features": 500, "ngram_range": (1, 2)},
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions3 = regressor3.fit_predict(df)
        print(f"✓ TF-IDF encoder: {len(predictions3)} predictions made")
    except Exception as e:
        print(f"✗ TF-IDF encoder failed: {e}")

def test_advanced_features():
    """Test advanced features like exogenous features, cross-attention, etc."""
    print("\n=== Testing Advanced Features ===")
    
    df = create_test_data(15)
    
    # Test 1: Exogenous features without cross-attention
    print("\n1. Testing exogenous features (direct concatenation)...")
    try:
        regressor1 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions1 = regressor1.fit_predict(df)
        print(f"✓ Exogenous features (direct): {len(predictions1)} predictions made")
    except Exception as e:
        print(f"✗ Exogenous features (direct) failed: {e}")
    
    # Test 2: Exogenous features with cross-attention
    print("\n2. Testing cross-attention...")
    try:
        regressor2 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            cross_attention_enabled=True,
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions2 = regressor2.fit_predict(df)
        print(f"✓ Cross-attention: {len(predictions2)} predictions made")
    except Exception as e:
        print(f"✗ Cross-attention failed: {e}")
    
    # Test 3: Feature mixing
    print("\n3. Testing feature mixing...")
    try:
        regressor3 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            feature_mixer=True,
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions3 = regressor3.fit_predict(df)
        print(f"✓ Feature mixing: {len(predictions3)} predictions made")
    except Exception as e:
        print(f"✗ Feature mixing failed: {e}")

def test_text_chunking():
    """Test text chunking functionality."""
    print("\n=== Testing Text Chunking ===")
    
    df = create_test_data(10)
    
    # Test chunking with different parameters
    print("\n1. Testing text chunking...")
    try:
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            chunk_info=(20, 5),  # 20 words per chunk, 5 word overlap
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        predictions = regressor.fit_predict(df)
        print(f"✓ Text chunking: {len(predictions)} predictions made")
    except Exception as e:
        print(f"✗ Text chunking failed: {e}")

def test_different_losses():
    """Test different loss functions."""
    print("\n=== Testing Different Loss Functions ===")
    
    df = create_test_data(10)
    
    losses_to_test = ["mae", "mse", "rmse", "smape", "mape", "wmape"]
    
    for loss in losses_to_test:
        print(f"\nTesting {loss.upper()} loss...")
        try:
            regressor = TextRegressor(
                model_name="lstm",
                encoder_model="sentence-transformers/all-MiniLM-L6-v2",
                loss_function=loss,
                max_steps=10,
                learning_rate=0.001,
                batch_size=4
            )
            predictions = regressor.fit_predict(df)
            print(f"✓ {loss.upper()} loss: {len(predictions)} predictions made")
        except Exception as e:
            print(f"✗ {loss.upper()} loss failed: {e}")

def test_model_persistence():
    """Test model save and load functionality."""
    print("\n=== Testing Model Persistence ===")
    
    df = create_test_data(10)
    
    try:
        # Create and train a model
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        
        # Fit the model
        regressor.fit(df)
        
        # Make predictions
        predictions1 = regressor.predict(df)
        
        # Save the model
        with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp_file:
            model_path = tmp_file.name
        
        regressor.model.save(model_path)
        print(f"✓ Model saved to {model_path}")
        
        # Load the model
        from textregress.models import get_model
        loaded_model = get_model("lstm").load(model_path)
        
        # Create new regressor with loaded model
        new_regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=10,
            learning_rate=0.001,
            batch_size=4
        )
        new_regressor.model = loaded_model
        new_regressor.encoder = regressor.encoder  # Copy encoder
        
        # Make predictions with loaded model
        predictions2 = new_regressor.predict(df)
        
        # Compare predictions (should be similar)
        diff = np.mean(np.abs(predictions1 - predictions2))
        print(f"✓ Model persistence: predictions differ by {diff:.6f}")
        
        # Clean up
        os.unlink(model_path)
        
    except Exception as e:
        print(f"✗ Model persistence failed: {e}")

def test_registry_systems():
    """Test the registry systems for models, encoders, and losses."""
    print("\n=== Testing Registry Systems ===")
    
    # Test model registry
    print("\n1. Testing model registry...")
    try:
        models = list_available_models()
        print(f"✓ Available models: {models}")
    except Exception as e:
        print(f"✗ Model registry failed: {e}")
    
    # Test encoder registry
    print("\n2. Testing encoder registry...")
    try:
        encoders = list_available_encoders()
        print(f"✓ Available encoders: {encoders}")
    except Exception as e:
        print(f"✗ Encoder registry failed: {e}")
    
    # Test loss registry
    print("\n3. Testing loss registry...")
    try:
        losses = list_available_losses()
        print(f"✓ Available losses: {losses}")
    except Exception as e:
        print(f"✗ Loss registry failed: {e}")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Testing Edge Cases ===")
    
    # Test with empty DataFrame
    print("\n1. Testing empty DataFrame...")
    try:
        empty_df = pd.DataFrame({'text': [], 'y': []})
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=5
        )
        regressor.fit(empty_df)
        print("✗ Should have raised error for empty DataFrame")
    except Exception as e:
        print(f"✓ Correctly handled empty DataFrame: {type(e).__name__}")
    
    # Test with missing columns
    print("\n2. Testing missing columns...")
    try:
        invalid_df = pd.DataFrame({'text': ['test'], 'wrong_column': [1.0]})
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=5
        )
        regressor.fit(invalid_df)
        print("✗ Should have raised error for missing 'y' column")
    except Exception as e:
        print(f"✓ Correctly handled missing columns: {type(e).__name__}")
    
    # Test with very short texts
    print("\n3. Testing very short texts...")
    try:
        short_df = pd.DataFrame({
            'text': ['a', 'b', 'c', 'd', 'e'],
            'y': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=5,
            learning_rate=0.001,
            batch_size=2
        )
        predictions = regressor.fit_predict(short_df)
        print(f"✓ Handled very short texts: {len(predictions)} predictions made")
    except Exception as e:
        print(f"✗ Failed with very short texts: {e}")

def main():
    """Run all comprehensive tests."""
    print("Starting comprehensive end-to-end test for textregress package...")
    print("=" * 60)
    
    # Test basic functionality
    test_basic_functionality()
    
    # Test advanced features
    test_advanced_features()
    
    # Test text chunking
    test_text_chunking()
    
    # Test different loss functions
    test_different_losses()
    
    # Test model persistence
    test_model_persistence()
    
    # Test registry systems
    test_registry_systems()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n" + "=" * 60)
    print("Comprehensive testing completed!")
    print("Check the output above for any failures (marked with ✗)")

if __name__ == "__main__":
    main() 