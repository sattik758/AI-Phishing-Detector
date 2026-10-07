import joblib
import pandas as pd

from pathlib import Path

from feature_extraction import extract_features


def load_model():

    project_root = Path(__file__).resolve().parent.parent

    model_path = (
        project_root
        / "model"
        / "phishing_model.pkl"
    )

    return joblib.load(model_path)


def predict_url(url, model):

    # Extract the same features used during training
    features = extract_features(url)

    # Convert dictionary to DataFrame
    feature_dataframe = pd.DataFrame([features])

    # Make prediction
    prediction = model.predict(
        feature_dataframe
    )[0]

    # Get probabilities
    probabilities = model.predict_proba(
        feature_dataframe
    )[0]

    # Class 0 = Legitimate
    # Class 1 = Phishing

    phishing_probability = probabilities[1]
    legitimate_probability = probabilities[0]

    if prediction == 1:
        result = "PHISHING"
    else:
        result = "LEGITIMATE"

    return (
        result,
        legitimate_probability,
        phishing_probability
    )


def main():

    print("=" * 60)
    print("AI-POWERED PHISHING URL DETECTOR")
    print("=" * 60)

    model = load_model()

    print("\nModel loaded successfully.")
    print("Enter 'exit' to quit.\n")

    while True:

        url = input("Enter URL: ").strip()

        if url.lower() == "exit":
            print("\nExiting...")
            break

        if not url:
            print("Please enter a URL.\n")
            continue

        try:

            result, legitimate_probability, phishing_probability = (
                predict_url(
                    url,
                    model
                )
            )

            print("\n" + "-" * 60)

            print(f"URL: {url}")

            print(f"Prediction: {result}")

            print(
                f"Legitimate probability: "
                f"{legitimate_probability * 100:.2f}%"
            )

            print(
                f"Phishing probability: "
                f"{phishing_probability * 100:.2f}%"
            )

            print("-" * 60 + "\n")

        except Exception as error:

            print(
                f"\nError while analyzing URL: {error}\n"
            )


if __name__ == "__main__":
    main()