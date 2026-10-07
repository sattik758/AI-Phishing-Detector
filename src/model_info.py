import joblib
from pathlib import Path


def main():

    project_root = Path(__file__).resolve().parent.parent

    model_path = (
        project_root
        / "model"
        / "phishing_model.pkl"
    )

    model = joblib.load(model_path)

    print("MODEL INFORMATION")
    print("=" * 50)

    print("Model:")
    print(model)

    print("\nNumber of trees:")
    print(model.n_estimators)

    print("\nNumber of features:")
    print(model.n_features_in_)

    print("\nClasses:")
    print(model.classes_)


if __name__ == "__main__":
    main()
    