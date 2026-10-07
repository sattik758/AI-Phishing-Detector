import pandas as pd
from pathlib import Path


def main():

    project_root = Path(__file__).resolve().parent.parent

    dataset_path = (
        project_root
        / "dataset"
        / "phishing_urls.csv"
    )

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    print("\n" + "=" * 60)
    print("DATASET INFORMATION")
    print("=" * 60)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f" - {column}")

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate URLs:")
    print(df["url"].duplicated().sum())

    print("\nLabel distribution:")
    print(df["label"].value_counts().sort_index())

    print("\nLabel percentages:")
    print(
        (df["label"].value_counts(normalize=True) * 100)
        .sort_index()
        .round(2)
    )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()