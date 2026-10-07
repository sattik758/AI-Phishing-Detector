import sys
import joblib
import pandas as pd
from pathlib import Path

from feature_extraction_v2 import extract_features_v2


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python src\\predict_v2.py <URL>")
        return

    url = sys.argv[1]

    project_root = Path(__file__).resolve().parent.parent
    model_path = project_root / "model" / "phishing_model_v2.pkl"

    print("Loading V2 model...")
    model = joblib.load(model_path)

    # Extract features
    features = extract_features_v2(url)

    # Convert dictionary -> DataFrame
    X = pd.DataFrame([features])

    # Make sure feature order matches training
    X = X[model.feature_names_in_]

    # Prediction
    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    legitimate_probability = probabilities[0]
    phishing_probability = probabilities[1]

    print("\nURL:")
    print(url)

    print("\nPrediction:")

    if prediction == 1:
        print("PHISHING")
    else:
        print("LEGITIMATE")

    print("\nProbabilities:")
    print(f"Legitimate: {legitimate_probability * 100:.2f}%")
    print(f"Phishing:   {phishing_probability * 100:.2f}%")

    print("\nImportant Features:")
    print(f"Brand similarity:    {features['brand_similarity']:.4f}")
    print(f"Brand lookalike:     {features['brand_lookalike_score']:.4f}")
    print(f"Digit substitution:  {features['has_digit_substitution']}")
    print(f"Exact brand match:   {features['exact_brand_match']}")
    print(f"HTTPS:               {features['uses_https']}")


if __name__ == "__main__":
    main()