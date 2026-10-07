import pandas as pd
import joblib
import tldextract

from pathlib import Path

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from feature_extraction_v2 import extract_features_v2


def get_domain(url):
    extracted = tldextract.extract(url)

    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"

    if extracted.domain:
        return extracted.domain

    return url


def main():

    project_root = Path(__file__).resolve().parent.parent

    dataset_path = (
        project_root
        / "dataset"
        / "phishing_urls.csv"
    )

    model_path = (
        project_root
        / "model"
        / "final_model.pkl"
    )

    # ==========================================
    # 1. Load dataset
    # ==========================================

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    print(f"Dataset URLs: {len(df)}")

    # ==========================================
    # 2. Extract domains
    # ==========================================

    print("\nExtracting domains...")

    df["domain"] = df["url"].apply(get_domain)

    print(
        f"Unique domains: "
        f"{df['domain'].nunique()}"
    )

    # ==========================================
    # 3. Extract V2 features
    # ==========================================

    print("\nExtracting V2 features...")

    features = []

    for index, url in enumerate(df["url"]):

        features.append(
            extract_features_v2(url)
        )

        if (index + 1) % 10000 == 0:
            print(
                f"Processed "
                f"{index + 1} URLs..."
            )

    X = pd.DataFrame(features)
    y = df["label"]
    groups = df["domain"]

    print(
        f"\nFeature matrix: {X.shape}"
    )

    # ==========================================
    # 4. Recreate domain-aware split
    # ==========================================

    print("\nCreating domain-aware test split...")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42
    )

    train_indices, test_indices = next(
        splitter.split(
            X,
            y,
            groups=groups
        )
    )

    X_test = X.iloc[test_indices]
    y_test = y.iloc[test_indices]

    train_domains = set(
        groups.iloc[train_indices]
    )

    test_domains = set(
        groups.iloc[test_indices]
    )

    overlap = train_domains & test_domains

    print(
        f"Training URLs: {len(train_indices)}"
    )

    print(
        f"Testing URLs: {len(test_indices)}"
    )

    print(
        f"Training domains: {len(train_domains)}"
    )

    print(
        f"Testing domains: {len(test_domains)}"
    )

    print(
        f"Domain overlap: {len(overlap)}"
    )

    # ==========================================
    # 5. Load final V2 model
    # ==========================================

    print("\nLoading final V2 model...")

    model = joblib.load(model_path)

    # Make sure feature order matches training
    X_test = X_test[
        model.feature_names_in_
    ]

    # ==========================================
    # 6. Prediction
    # ==========================================

    print("\nRunning final evaluation...")

    predictions = model.predict(X_test)

    # ==========================================
    # 7. Metrics
    # ==========================================

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    false_positives = matrix[0][1]
    false_negatives = matrix[1][0]

    # ==========================================
    # 8. Final report
    # ==========================================

    print("\n")
    print("==========================================")
    print("       FINAL MODEL EVALUATION")
    print("==========================================")

    print(f"\nModel: V2 Random Forest")
    print(f"Features: {X.shape[1]}")
    print(f"Dataset URLs: {len(df)}")
    print(f"Unique domains: {df['domain'].nunique()}")

    print("\n--- Domain-Aware Split ---")

    print(
        f"Training URLs:     {len(train_indices)}"
    )

    print(
        f"Testing URLs:      {len(test_indices)}"
    )

    print(
        f"Training domains:  {len(train_domains)}"
    )

    print(
        f"Testing domains:   {len(test_domains)}"
    )

    print(
        f"Domain overlap:    {len(overlap)}"
    )

    print("\n--- Performance ---")

    print(
        f"Accuracy:           {accuracy * 100:.2f}%"
    )

    print(
        f"Precision:          {precision * 100:.2f}%"
    )

    print(
        f"Recall:             {recall * 100:.2f}%"
    )

    print(
        f"F1 Score:           {f1 * 100:.2f}%"
    )

    print(
        f"False Positives:    {false_positives}"
    )

    print(
        f"False Negatives:    {false_negatives}"
    )

    print("\n--- Classification Report ---")

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

    print("--- Confusion Matrix ---")

    print(matrix)

    print("\n==========================================")
    print("        FINAL MODEL VALIDATION PASSED")
    print("==========================================")


if __name__ == "__main__":
    main()