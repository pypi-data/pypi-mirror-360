import pandas as pd
from textregress import TextRegressor

print("1. Starting minimal test...")

# Create minimal data
data = {
    "text": ["Test text one.", "Test text two."],
    "y": [1.0, 2.0]
}
df = pd.DataFrame(data)

print("2. DataFrame created...")

# Create minimal TextRegressor
regressor = TextRegressor(
    model_name="lstm",
    encoder_model="tfidf",
    max_steps=1,
    early_stop_enabled=False
)

print("3. TextRegressor created...")

# Try to fit
regressor.fit(df)

print("4. Fit completed...")

# Try to predict
predictions = regressor.predict(df)

print("5. Predictions:", predictions)
print("6. Test completed successfully!") 