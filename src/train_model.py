import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from feature_extraction import extract_features


def main():

    # ---------------------------------------------
    # 1. Locate project directories
    # ---------------------------------------------

    project_root = Path(__file__).resolve().parent.parent

    dataset_path = (
        project_root
        / "dataset"
        / "phishing_urls.csv"
    )

    model_directory = project_root / "model"

    model_directory.mkdir(
        exist_ok=True
    )

    model_path = (
        model_directory
        / "phishing_model.pkl"
    )

    # ---------------------------------------------
    # 2. Load dataset
    # ---------------------------------------------

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    print(f"Total URLs: {len(df)}")

    # ---------------------------------------------
    # 3. Extract features
    # ---------------------------------------------

    print("\nExtracting URL features...")

    feature_data = []

    for index, url in enumerate(df["url"]):

        feature_data.append(
            extract_features(url)
        )

        # Progress indicator
        if (index + 1) % 10000 == 0:
            print(
                f"Processed {index + 1} URLs..."
            )

    X = pd.DataFrame(feature_data)

    y = df["label"]

    print("\nFeature extraction completed.")

    print(
        f"Feature matrix shape: {X.shape}"
    )

    # ---------------------------------------------
    # 4. Train/Test split
    # ---------------------------------------------

    print("\nSplitting dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # ---------------------------------------------
    # 5. Create Random Forest
    # ---------------------------------------------

    print("\nCreating Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    # ---------------------------------------------
    # 6. Train
    # ---------------------------------------------

    print("\nTraining model...")

    model.fit(
        X_train,
        y_train
    )

    print("Training completed.")

    # ---------------------------------------------
    # 7. Predictions
    # ---------------------------------------------

    print("\nEvaluating model...")

    predictions = model.predict(
        X_test
    )

    # ---------------------------------------------
    # 8. Accuracy
    # ---------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"\nAccuracy: {accuracy * 100:.2f}%"
    )

    # ---------------------------------------------
    # 9. Classification report
    # ---------------------------------------------

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Legitimate",
                "Phishing"
            ]
        )
    )

    # ---------------------------------------------
    # 10. Confusion matrix
    # ---------------------------------------------

    print("\nConfusion Matrix:")

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    print(matrix)

    # ---------------------------------------------
    # 11. Feature importance
    # ---------------------------------------------

    print("\nFeature Importance:")

    importance = pd.Series(
        model.feature_importances_,
        index=X.columns
    )

    importance = importance.sort_values(
        ascending=False
    )

    print(importance)

    # ---------------------------------------------
    # 12. Save model
    # ---------------------------------------------

    joblib.dump(
        model,
        model_path
    )

    print(
        f"\nModel saved to:\n{model_path}"
    )


if __name__ == "__main__":
    main()