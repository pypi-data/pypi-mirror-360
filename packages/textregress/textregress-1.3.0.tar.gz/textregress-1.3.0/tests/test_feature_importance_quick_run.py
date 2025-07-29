import pandas as pd
from textregress import TextRegressor

# Create sample data
data = {
    'text': [
        "This is a positive review about the product.",
        "The quality is excellent and I recommend it.",
        "Not satisfied with the purchase.",
        "Great value for money."
    ],
    'y': [4.5, 4.8, 2.1, 4.2],
    'feature1': [1.0, 1.2, 0.8, 1.1],
    'feature2': [0.5, 0.6, 0.3, 0.7]
}
df = pd.DataFrame(data)

# Create and train the model
regressor = TextRegressor(
    model_name="lstm",  # or "gru"
    encoder_model="sentence-transformers/all-MiniLM-L6-v2",
    exogenous_features=["feature1", "feature2"],
    cross_attention_enabled=True,
    max_steps=100
)

# Fit and predict
predictions = regressor.fit_predict(df)
print(f"Predictions: {predictions}") # Basic usage
importance = regressor.get_feature_importance()
print(importance['text_importance'].shape)  # (n_samples, seq_len)
print(importance['exogenous_importance'].shape)  # (n_samples, n_features)
print(importance) 