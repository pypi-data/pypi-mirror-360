#!/usr/bin/env python3
"""
Test the new get_feature_importance method.
"""

import pandas as pd
import numpy as np
from textregress import TextRegressor

def test_feature_importance():
    """Test the get_feature_importance method."""
    print("Testing get_feature_importance method...")
    
    # Create test data
    data = {
        'text': [
            "This is a positive review about the product quality.",
            "The customer service was excellent and helpful.",
            "Not satisfied with the purchase experience."
        ],
        'y': [4.5, 4.8, 2.1],
        'feature1': [1.0, 1.2, 0.8],
        'feature2': [0.5, 0.6, 0.3]
    }
    df = pd.DataFrame(data)
    
    # Test 1: Basic gradient importance without exogenous features
    print("\n1. Testing gradient importance without exogenous features...")
    try:
        regressor1 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            max_steps=10,
            learning_rate=0.001,
            batch_size=2
        )
        regressor1.fit(df)
        
        # Get feature importance for training data
        importance1 = regressor1.get_feature_importance()
        print(f"✓ Gradient importance shape: {importance1['text_importance'].shape}")
        
        # Get feature importance for specific data
        test_df = df.head(2)
        importance1_test = regressor1.get_feature_importance(test_df)
        print(f"✓ Test data importance shape: {importance1_test['text_importance'].shape}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Gradient importance with exogenous features
    print("\n2. Testing gradient importance with exogenous features...")
    try:
        regressor2 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            max_steps=10,
            learning_rate=0.001,
            batch_size=2
        )
        regressor2.fit(df)
        
        importance2 = regressor2.get_feature_importance()
        print(f"✓ Text importance shape: {importance2['text_importance'].shape}")
        print(f"✓ Exogenous importance shape: {importance2['exogenous_importance'].shape}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 3: Attention mode with cross-attention
    print("\n3. Testing attention mode with cross-attention...")
    try:
        regressor3 = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2",
            exogenous_features=["feature1", "feature2"],
            cross_attention_enabled=True,
            max_steps=10,
            learning_rate=0.001,
            batch_size=2
        )
        regressor3.fit(df)
        
        attention_importance = regressor3.get_feature_importance(mode="attention")
        print(f"✓ Attention importance shape: {attention_importance['text_importance'].shape}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 4: Error handling
    print("\n4. Testing error handling...")
    try:
        # Test with unfitted model
        unfitted_regressor = TextRegressor(
            model_name="lstm",
            encoder_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        unfitted_regressor.get_feature_importance()
        print("✗ Should have raised error for unfitted model")
    except Exception as e:
        print(f"✓ Correctly handled unfitted model: {type(e).__name__}")
    
    try:
        # Test invalid mode
        regressor1.get_feature_importance(mode="invalid")
        print("✗ Should have raised error for invalid mode")
    except Exception as e:
        print(f"✓ Correctly handled invalid mode: {type(e).__name__}")
    
    try:
        # Test attention mode without exogenous features
        regressor1.get_feature_importance(mode="attention")
        print("✗ Should have raised error for attention without exogenous features")
    except Exception as e:
        print(f"✓ Correctly handled attention without exogenous features: {type(e).__name__}")
    
    print("\n=== Feature importance testing completed! ===")

if __name__ == "__main__":
    test_feature_importance() 