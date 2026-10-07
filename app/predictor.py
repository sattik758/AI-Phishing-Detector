import joblib
import pandas as pd
from pathlib import Path

from src.feature_extraction_v2 import extract_features_v2


# ==========================================
# Load final model
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "model"
    / "final_model.pkl"
)

model = joblib.load(MODEL_PATH)


# ==========================================
# Generate human-readable explanation
# ==========================================

def generate_explanation(features):

    signals = []

    # URL length
    if features["url_length"] >= 100:
        signals.append(
            "Very long URL structure"
        )

    # Path depth
    if features["path_depth"] >= 4:
        signals.append(
            "Deep URL path structure"
        )

    # Digits
    if features["hostname_digit_count"] >= 2:
        signals.append(
            "Multiple digits in hostname"
        )

    # Hyphens
    if features["domain_hyphen_count"] >= 2:
        signals.append(
            "Multiple hyphens in domain"
        )

    # Suspicious words
    if features["suspicious_word_count"] > 0:
        signals.append(
            "Contains suspicious security-related words"
        )

    # IP address
    if features["has_ip"] == 1:
        signals.append(
            "Uses an IP address instead of a normal domain"
        )

    # Punycode
    if features["has_punycode"] == 1:
        signals.append(
            "Uses punycode in the domain"
        )

    # Percent encoding
    if features["has_percent_encoding"] == 1:
        signals.append(
            "Contains percent-encoded characters"
        )

    # Digit substitution / lookalike domain
    if features["has_digit_substitution"] == 1:
        signals.append(
            "Possible digit-based domain lookalike"
        )

    # Brand lookalike
    if features["brand_lookalike_score"] > 0:
        signals.append(
            "Domain resembles a known brand"
        )

    # If no suspicious signals were found
    if not signals:
        signals.append(
            "No major suspicious URL characteristics detected"
        )

    return signals


# ==========================================
# Prediction function
# ==========================================

def predict_url(url):

    # Extract V2 features
    features = extract_features_v2(url)

    # Convert dictionary to DataFrame
    X = pd.DataFrame([features])

    # Match training feature order
    X = X[model.feature_names_in_]

    # Prediction
    prediction = model.predict(X)[0]

    # Probability
    probabilities = model.predict_proba(X)[0]

    legitimate_probability = float(
        probabilities[0]
    )

    phishing_probability = float(
        probabilities[1]
    )

    # ======================================
    # Risk classification
    # ======================================

    if phishing_probability >= 0.75:
        risk = "HIGH"

    elif phishing_probability >= 0.40:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    # ======================================
    # Generate explanation
    # ======================================

    explanation = generate_explanation(features)

    # ======================================
    # Result
    # ======================================

    return {
        "url": url,
        "prediction": (
            "PHISHING"
            if prediction == 1
            else "LEGITIMATE"
        ),
        "legitimate_probability":
            legitimate_probability,
        "phishing_probability":
            phishing_probability,
        "risk": risk,
        "explanation": explanation
    }