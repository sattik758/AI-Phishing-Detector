import pandas as pd
import tldextract

from pathlib import Path

from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from feature_extraction import extract_features
from feature_extraction_v2 import extract_features_v2


def get_domain(url):
    extracted = tldextract.extract(url)

    if extracted.domain and extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"

    if extracted.domain:
        return extracted.domain

    return url


def evaluate_model(name, model, X_test, y_test):

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

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

    print("\n================================")
    print(name)
    print("================================")

    print(f"Accuracy:          {accuracy * 100:.2f}%")
    print(f"Precision:         {precision * 100:.2f}%")
    print(f"Recall:            {recall * 100:.2f}%")
    print(f"F1 Score:          {f1 * 100:.2f}%")
    print(f"False Positives:   {false_positives}")
    print(f"False Negatives:   {false_negatives}")

    print("\nConfusion Matrix:")
    print(matrix)

    return {
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "False Positives": false_positives,
        "False Negatives": false_negatives
    }


def main():

    project_root = Path(__file__).resolve().parent.parent

    dataset_path = (
        project_root
        / "dataset"
        / "phishing_urls.csv"
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

    print(
        f"Unique domains: "
        f"{df['domain'].nunique()}"
    )

    # ==========================================
    # 3. Extract V1 features
    # ==========================================

    print("\nExtracting V1 features...")

    v1_features = []

    for index, url in enumerate(df["url"]):

        v1_features.append(
            extract_features(url)
        )

        if (index + 1) % 10000 == 0:
            print(
                f"V1 processed "
                f"{index + 1} URLs..."
            )

    X_v1 = pd.DataFrame(v1_features)

    print(
        f"V1 feature matrix: "
        f"{X_v1.shape}"
    )

    # ==========================================
    # 4. Extract V2 features
    # ==========================================

    print("\nExtracting V2 features...")

    v2_features = []

    for index, url in enumerate(df["url"]):

        v2_features.append(
            extract_features_v2(url)
        )

        if (index + 1) % 10000 == 0:
            print(
                f"V2 processed "
                f"{index + 1} URLs..."
            )

    X_v2 = pd.DataFrame(v2_features)

    print(
        f"V2 feature matrix: "
        f"{X_v2.shape}"
    )

    y = df["label"]
    groups = df["domain"]

    # ==========================================
    # 5. Create SAME domain-aware split
    # ==========================================

    print("\nCreating common domain-aware split...")

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.20,
        random_state=42
    )

    train_indices, test_indices = next(
        splitter.split(
            X_v1,
            y,
            groups=groups
        )
    )

    X_v1_train = X_v1.iloc[train_indices]
    X_v1_test = X_v1.iloc[test_indices]

    X_v2_train = X_v2.iloc[train_indices]
    X_v2_test = X_v2.iloc[test_indices]

    y_train = y.iloc[train_indices]
    y_test = y.iloc[test_indices]

    print(
        f"\nTraining URLs: "
        f"{len(train_indices)}"
    )

    print(
        f"Testing URLs: "
        f"{len(test_indices)}"
    )

    print(
        f"Training domains: "
        f"{groups.iloc[train_indices].nunique()}"
    )

    print(
        f"Testing domains: "
        f"{groups.iloc[test_indices].nunique()}"
    )

    # ==========================================
    # 6. Train V1
    # ==========================================

    print("\n================================")
    print("Training V1 model")
    print("================================")

    v1_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    v1_model.fit(
        X_v1_train,
        y_train
    )

    print("V1 training completed.")

    # ==========================================
    # 7. Train V2
    # ==========================================

    print("\n================================")
    print("Training V2 model")
    print("================================")

    v2_model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    v2_model.fit(
        X_v2_train,
        y_train
    )

    print("V2 training completed.")

    # ==========================================
    # 8. Evaluate both
    # ==========================================

    v1_results = evaluate_model(
        "V1 Random Forest",
        v1_model,
        X_v1_test,
        y_test
    )

    v2_results = evaluate_model(
        "V2 Random Forest",
        v2_model,
        X_v2_test,
        y_test
    )

    # ==========================================
    # 9. Comparison table
    # ==========================================

    comparison = pd.DataFrame([
        v1_results,
        v2_results
    ])

    print("\n\n================================")
    print("V1 vs V2 COMPARISON")
    print("================================")

    print(
        comparison.to_string(
            index=False,
            formatters={
                "Accuracy": "{:.4f}".format,
                "Precision": "{:.4f}".format,
                "Recall": "{:.4f}".format,
                "F1": "{:.4f}".format
            }
        )
    )


if __name__ == "__main__":
    main()