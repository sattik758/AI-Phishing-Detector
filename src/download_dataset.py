from ucimlrepo import fetch_ucirepo
import pandas as pd
from pathlib import Path


def main():

    print("Downloading PhiUSIIL dataset...")

    dataset = fetch_ucirepo(id=967)

    features = dataset.data.features
    targets = dataset.data.targets

    df = pd.concat(
        [features, targets],
        axis=1
    )

    # Keep only the columns we need for our project
    df = df[["URL", "label"]]

    # Rename columns
    df = df.rename(
        columns={
            "URL": "url",
            "label": "original_label"
        }
    )

    # Convert UCI labels:
    # UCI: 1 = legitimate, 0 = phishing
    #
    # Our project:
    # 0 = legitimate, 1 = phishing

    df["label"] = df["original_label"].map({
        1: 0,
        0: 1
    })

    df = df.drop(columns=["original_label"])

    # Remove missing URLs
    df = df.dropna(subset=["url"])

    # Remove duplicate URLs
    df = df.drop_duplicates(subset=["url"])

    project_root = Path(__file__).resolve().parent.parent

    output_path = project_root / "dataset" / "phishing_urls.csv"

    df.to_csv(
        output_path,
        index=False
    )

    print("\nDataset downloaded successfully!")

    print(f"Total URLs: {len(df)}")

    print("\nClass distribution:")

    print(
        df["label"]
        .value_counts()
        .sort_index()
    )

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()