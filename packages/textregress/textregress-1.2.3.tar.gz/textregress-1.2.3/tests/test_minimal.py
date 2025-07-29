#!/usr/bin/env python3
"""
Minimal test to identify TextRegressor issues
"""

import pandas as pd
import sys
import traceback

print("Starting minimal test...")

try:
    print("1. Importing textregress...")
    from textregress import TextRegressor
    print("✓ Import successful")
    
    print("2. Creating sample data...")
    data = {
        'text': ["This is a test.", "Another test sentence."],
        'y': [1.0, 2.0]
    }
    df = pd.DataFrame(data)
    print("✓ Data created")
    
    print("3. Creating TextRegressor...")
    regressor = TextRegressor(
        model_name="lstm",
        encoder_model="tfidf",
        max_steps=2,
        early_stop_enabled=False
    )
    print("✓ TextRegressor created")
    
    print("4. Testing fit...")
    regressor.fit(df)
    print("✓ Fit successful")
    
    print("5. Testing predict...")
    predictions = regressor.predict(df)
    print(f"✓ Predictions: {predictions}")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1) 