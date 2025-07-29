#!/usr/bin/env python3
"""
Ultimate test for TextRegressor: large/long data, all parameters, all functions, and performance logging.
"""

import pandas as pd
import numpy as np
import time
import traceback
from textregress import TextRegressor

# Utility for logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.info

def generate_long_text(base, repeat=100):
    return " ".join([base] * repeat)

def main():
    try:
        log("=" * 80)
        log("ULTIMATE TEXTREGRESS TEST STARTING")
        log("=" * 80)
        
        log("STEP 1: Generating large and long synthetic dataset...")
        t0 = time.time()
        N = 100  # Number of samples
        long_texts = [generate_long_text(f"Sample {i} text for ultimate test.", repeat=100) for i in range(N)]
        y = np.random.uniform(1, 5, size=N)
        ex1 = np.random.normal(0, 1, size=N)
        ex2 = np.random.randint(0, 100, size=N)
        ex3 = np.random.uniform(10, 20, size=N)
        ex4 = np.random.binomial(1, 0.5, size=N)
        df = pd.DataFrame({
            'text': long_texts,
            'y': y,
            'ex1': ex1,
            'ex2': ex2,
            'ex3': ex3,
            'ex4': ex4
        })
        t1 = time.time()
        log(f"✓ Dataset generated in {t1-t0:.2f}s")
        log(f"  DataFrame shape: {df.shape}")
        log(f"  First text sample: {df['text'][0][:100]}...")
        log(f"  Target range: {df['y'].min():.2f} to {df['y'].max():.2f}")

        log("\nSTEP 2: Setting up all possible parameters...")
        # All possible parameters (removed rnn_type as it's redundant with model_name)
        params = dict(
            model_name="lstm",
            encoder_model="tfidf",
            encoder_params={"max_features": 500, "ngram_range": (1, 2)},
            chunk_info=(50, 10),
            padding_value=0,
            exogenous_features=["ex1", "ex2", "ex3", "ex4"],
            learning_rate=0.005,
            loss_function="mse",
            max_steps=20,
            early_stop_enabled=True,
            patience_steps=5,
            val_check_steps=2,
            optimizer_name="adam",
            optimizer_params={"weight_decay": 0.01},
            random_seed=123,
            rnn_layers=2,
            hidden_size=64,
            bidirectional=True,
            inference_layer_units=32,
            cross_attention_enabled=True,
            dropout_rate=0.2,
            se_layer=True,
            feature_mixer=True
        )
        log(f"✓ Parameters configured: {len(params)} parameters")
        log(f"  Model: {params['model_name']}, Encoder: {params['encoder_model']}")
        log(f"  Chunking: {params['chunk_info']}, Features: {len(params['exogenous_features'])}")

        log("\nSTEP 3: Instantiating TextRegressor...")
        t0 = time.time()
        regressor = TextRegressor(**params)
        t1 = time.time()
        log(f"✓ TextRegressor instantiated in {t1-t0:.2f}s")

        # Test fit
        log("\nSTEP 4: Fitting model...")
        t0 = time.time()
        regressor.fit(df, batch_size=8, val_size=0.2)
        t1 = time.time()
        log(f"✓ Model fit complete in {t1-t0:.2f}s")

        # Test predict
        log("\nSTEP 5: Predicting on training data...")
        t0 = time.time()
        preds = regressor.predict(df, batch_size=8)
        t1 = time.time()
        log(f"✓ Prediction complete in {t1-t0:.2f}s")
        log(f"  Predictions shape: {preds.shape}, dtype: {preds.dtype}")
        log(f"  First 5 predictions: {preds[:5]}")
        log(f"  Prediction range: {preds.min():.2f} to {preds.max():.2f}")

        # Test fit_predict
        log("\nSTEP 6: Testing fit_predict...")
        t0 = time.time()
        preds2 = regressor.fit_predict(df, batch_size=8, val_size=0.2)
        t1 = time.time()
        log(f"✓ fit_predict complete in {t1-t0:.2f}s")
        log(f"  fit_predict output shape: {preds2.shape}")

        # Test save/load
        log("\nSTEP 7: Testing save/load functionality...")
        t0 = time.time()
        regressor.save("ultimate_model.pt")
        t1 = time.time()
        log(f"✓ Model saved in {t1-t0:.2f}s")
        
        t0 = time.time()
        loaded = TextRegressor(**params)
        loaded.load("ultimate_model.pt")
        t1 = time.time()
        log(f"✓ Model loaded in {t1-t0:.2f}s")
        
        t0 = time.time()
        preds_loaded = loaded.predict(df, batch_size=8)
        t1 = time.time()
        log(f"✓ Loaded model prediction in {t1-t0:.2f}s")
        log(f"  Loaded model predictions shape: {preds_loaded.shape}")

        # Test embedding extraction
        log("\nSTEP 8: Testing embedding extraction...")
        t0 = time.time()
        emb = regressor.model.get_document_embedding(df['text'].tolist())
        t1 = time.time()
        log(f"✓ Document embedding extracted in {t1-t0:.2f}s")
        log(f"  Document embedding shape: {emb.shape}")
        
        t0 = time.time()
        seq_emb = regressor.model.get_sequence_embeddings(df['text'].tolist())
        t1 = time.time()
        log(f"✓ Sequence embeddings extracted in {t1-t0:.2f}s")
        log(f"  Sequence embeddings: {type(seq_emb)}, length: {len(seq_emb)}")

        # Test explainability (if available)
        log("\nSTEP 9: Testing explainability...")
        if hasattr(regressor.model, 'explain_text'):
            t0 = time.time()
            explanation = regressor.model.explain_text(df['text'][0])
            t1 = time.time()
            log(f"✓ Text explanation generated in {t1-t0:.2f}s")
            log(f"  Explanation for first text: {explanation}")
        else:
            log("  explain_text not available on model.")

        # Test all registry functions
        log("\nSTEP 10: Testing registry functions...")
        from textregress.models import list_available_models
        from textregress.encoders import list_available_encoders
        from textregress.losses import list_available_losses
        log(f"  Available models: {list_available_models()}")
        log(f"  Available encoders: {list_available_encoders()}")
        log(f"  Available losses: {list_available_losses()}")

        log("\n" + "=" * 80)
        log("🎉 ALL ULTIMATE TESTS COMPLETED SUCCESSFULLY! 🎉")
        log("=" * 80)
        
    except Exception as e:
        log(f"\n❌ Exception occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 