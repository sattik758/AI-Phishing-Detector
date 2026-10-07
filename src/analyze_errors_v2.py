import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split

from feature_extraction_v2 import extract_features_v2


def main():

    project_root = Path(__file__).resolve().parent.parent

    dataset_path = project_root / "dataset" / "phishing_urls.csv"
    model_path = project_root / "model" / "phishing_model_v2.pkl"

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)

    print(f"Total URLs: {len(df)}")

    # -----------------------------
    # Extract features
    # -----------------------------

    print("\nExtracting V2 features...")

    feature_data = []

    for index, url in enumerate(df["url"]):

        feature_data.append(
            extract_features_v2(url)
        )

        if (index + 1) % 10000 == 0:
            print(f"Processed {index + 1} URLs...")

    X = pd.DataFrame(feature_data)
    y = df["label"]

    # -----------------------------
    # Same train/test split
    # -----------------------------

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # Get corresponding URLs
    _, url_test, _, _ = train_test_split(
        df["url"],
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # -----------------------------
    # Load model
    # -----------------------------

    print("\nLoading V2 model...")

    model = joblib.load(model_path)

    # Ensure feature order
    X_test = X_test[model.feature_names_in_]

    # -----------------------------
    # Predictions
    # -----------------------------

    predictions = model.predict(X_test)

    probabilities = model.predict_proba(X_test)

    phishing_probability = probabilities[:, 1]

    # -----------------------------
    # Error analysis
    # -----------------------------

    results = pd.DataFrame({
        "url": url_test.values,
        "actual": y_test.values,
        "predicted": predictions,
        "phishing_probability": phishing_probability
    })

    # False negatives
    false_negatives = results[
        (results["actual"] == 1) &
        (results["predicted"] == 0)
    ]

    # False positives
    false_positives = results[
        (results["actual"] == 0) &
        (results["predicted"] == 1)
    ]

    print("\n==============================")
    print("ERROR ANALYSIS")
    print("==============================")

    print(f"\nFalse Negatives: {len(false_negatives)}")
    print(f"False Positives: {len(false_positives)}")

    # -----------------------------
    # Show false negatives
    # -----------------------------

    print("\n==============================")
    print("FALSE NEGATIVES")
    print("==============================")

    print(
        false_negatives[
            ["url", "phishing_probability"]
        ]
        .sort_values(
            "phishing_probability"
        )
        .head(20)
        .to_string(index=False)
    )

    # -----------------------------
    # Show false positives
    # -----------------------------

    print("\n==============================")
    print("FALSE POSITIVES")
    print("==============================")

    print(
        false_positives[
            ["url", "phishing_probability"]
        ]
        .sort_values(
            "phishing_probability",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()