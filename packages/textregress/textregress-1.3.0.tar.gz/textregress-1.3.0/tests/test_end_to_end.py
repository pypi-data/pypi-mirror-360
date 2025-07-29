import pandas as pd
from textregress import TextRegressor
import numpy as np
import traceback

def main():
    print("Creating dummy DataFrame...")
    data = {
        "text": [
            "This is record one testing TextRegressor capabilities.",
            "Record two provides another example with a different text.",
            "The third record comes with its unique sentence structure.",
            "This is the fourth record which is slightly longer than the previous ones.",
            "Fifth record is here to test the robustness of our model.",
            "The sixth record contains simple language for easy testing.",
            "Seventh record brings a bit more complexity in wording and structure.",
            "The eighth record is designed to examine the model's handling of diverse texts.",
            "Ninth record includes a mixture of short and long phrases.",
            "Tenth record finally rounds out our dataset for thorough testing."
        ],
        "y": [1.2, 2.3, 1.8, 2.0, 1.5, 2.1, 1.9, 2.5, 1.7, 2.2],
        "ex1": [0.5, 1.0, 0.8, 0.6, 1.2, 0.7, 1.1, 0.9, 0.4, 1.3],
        "ex2": [10, 20, 15, 18, 22, 14, 19, 17, 16, 21]
    }
    df = pd.DataFrame(data)
    print("Dummy DataFrame created.")

    # Parameters
    batch_size = 4
    val_size = 0.2

    print("Instantiating TextRegressor...")
    regressor = TextRegressor(
        model_name="lstm",
        encoder_model="tfidf",
        chunk_info=(6, 0),
        padding_value=0,
        exogenous_features=["ex1", "ex2"],
        learning_rate=0.01,
        loss_function="mae",
        max_steps=5,
        early_stop_enabled=False,
        patience_steps=3,
        val_check_steps=1,
        optimizer_name="adam",
        random_seed=42
    )
    print("TextRegressor instantiated.")

    # Fit the model
    print("[DEBUG] Calling fit()...")
    try:
        regressor.fit(df, batch_size=batch_size, val_size=val_size)
        print("[DEBUG] fit() completed.")
    except Exception as e:
        print(f"[DEBUG] Exception in fit(): {e}")
        traceback.print_exc()
        return

    # Predict
    print("[DEBUG] Calling predict()...")
    try:
        predictions = regressor.predict(df, batch_size=batch_size)
        print("[DEBUG] predict() completed.")
        print("Predictions:", predictions)
    except Exception as e:
        print(f"[DEBUG] Exception in predict(): {e}")
        traceback.print_exc()
        return

    # Assertions
    assert isinstance(predictions, np.ndarray), "Predictions should be a numpy array."
    assert predictions.shape[0] == df.shape[0], f"Expected {df.shape[0]} predictions, got {predictions.shape[0]}"
    print("Assertions passed.")

    # Optionally print model summary if available
    if hasattr(regressor, 'model') and regressor.model is not None:
        print("Model summary:")
        try:
            print(regressor.model)
        except Exception:
            print("(Could not print model summary)")

if __name__ == "__main__":
    try:
        main()
        print("\nEnd-to-end test completed successfully!\n")
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        traceback.print_exc() 