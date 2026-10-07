import pandas as pd
import joblib
import tldextract

from pathlib import Path

from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from feature_extraction_v2 import extract_features_v2


def get_domain(url):
    """
    Extract the registered domain from a URL.
    Used for grouping URLs during domain-aware splitting.
    """

    extracted = tldextract.extract(url)

    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"

    if extracted.domain:
        return extracted.domain

    return url


def main():

    project_root = Path(__file__).resolve().parent.parent

    dataset_path = project_root / "dataset" / "phishing_urls.csv"
    model_directory = project_root / "model"
    model_directory.mkdir(exist_ok=True)

    domain_model_path = (
        model_directory / "phishing_model_v2_domain_split.pkl"
    )

    # ==========================================
    # 1. Load dataset
    # ==========================================

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    print(f"Total URLs: {len(df)}")

    # ==========================================
    # 2. Extract domains
    # ==========================================

    print("\nExtracting domains...")

    df["domain"] = df["url"].apply(get_domain)

    print(f"Unique domains: {df['domain'].nunique()}")

    # ==========================================
    # 3. Extract V2 features
    # ==========================================

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
    groups = df["domain"]

    print("\nFeature extraction completed.")
    print(f"Feature matrix shape: {X.shape}")

    # ==========================================
    # 4. Domain-aware train/test split
    # ==========================================

    print("\nCreating domain-aware split...")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42
    )

    train_indices, test_indices = next(
        splitter.split(X, y, groups=groups)
    )

    X_train = X.iloc[train_indices]
    X_test = X.iloc[test_indices]

    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]

    train_domains = groups.iloc[train_indices]
    test_domains = groups.iloc[test_indices]

    print("\nSplit completed.")

    print(f"Training URLs: {len(X_train)}")
    print(f"Testing URLs:  {len(X_test)}")

    print(f"Training domains: {train_domains.nunique()}")
    print(f"Testing domains:  {test_domains.nunique()}")

    # ==========================================
    # 5. Verify domain separation
    # ==========================================

    overlap = set(train_domains) & set(test_domains)

    print(f"\nDomain overlap: {len(overlap)}")

    if len(overlap) == 0:
        print("SUCCESS: No domain appears in both train and test.")
    else:
        print("WARNING: Domain overlap detected!")

    # ==========================================
    # 6. Create model
    # ==========================================

    print("\nCreating domain-aware Random Forest...")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    # ==========================================
    # 7. Train
    # ==========================================

    print("\nTraining model...")

    model.fit(X_train, y_train)

    print("Training completed.")

    # ==========================================
    # 8. Evaluate
    # ==========================================

    print("\nEvaluating domain-aware model...")

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\n================================")
    print("DOMAIN-AWARE RESULTS")
    print("================================")

    print(
        f"\nAccuracy: {accuracy * 100:.2f}%"
    )

    # ==========================================
    # 9. Classification report
    # ==========================================

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

    # ==========================================
    # 10. Confusion matrix
    # ==========================================

    print("\nConfusion Matrix:")

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    print(matrix)

    # ==========================================
    # 11. Feature importance
    # ==========================================

    print("\nFeature Importance:")

    importance = pd.Series(
        model.feature_importances_,
        index=X.columns
    ).sort_values(
        ascending=False
    )

    print(importance)

    # ==========================================
    # 12. Save domain-aware model
    # ==========================================

    joblib.dump(
        model,
        domain_model_path
    )

    print(
        f"\nDomain-aware model saved to:\n"
        f"{domain_model_path}"
    )


if __name__ == "__main__":
    main()