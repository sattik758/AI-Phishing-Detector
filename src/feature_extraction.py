import re
import tldextract
from urllib.parse import urlparse


def extract_features(url):
    """
    Extract numerical features from a URL.
    These features will later be used by our ML model.
    """

    features = {}

    # Parse URL
    parsed = urlparse(url)

    # Extract domain information
    extracted = tldextract.extract(url)

    hostname = parsed.hostname or ""

    # ------------------------------------------------
    # 1. Basic URL features
    # ------------------------------------------------

    features["url_length"] = len(url)
    features["hostname_length"] = len(hostname)

    # ------------------------------------------------
    # 2. Character-based features
    # ------------------------------------------------

    features["dot_count"] = url.count(".")
    features["hyphen_count"] = url.count("-")
    features["underscore_count"] = url.count("_")
    features["slash_count"] = url.count("/")
    features["question_count"] = url.count("?")
    features["equal_count"] = url.count("=")
    features["at_count"] = url.count("@")
    features["ampersand_count"] = url.count("&")
    features["percent_count"] = url.count("%")

    # ------------------------------------------------
    # 3. Numbers and letters
    # ------------------------------------------------

    features["digit_count"] = sum(
        character.isdigit() for character in url
    )

    features["letter_count"] = sum(
        character.isalpha() for character in url
    )

    # ------------------------------------------------
    # 4. HTTPS
    # ------------------------------------------------

    features["uses_https"] = int(
        parsed.scheme.lower() == "https"
    )

    # ------------------------------------------------
    # 5. IP address detection
    # ------------------------------------------------

    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    features["has_ip"] = int(
        bool(re.match(ip_pattern, hostname))
    )

    # ------------------------------------------------
    # 6. @ symbol
    # ------------------------------------------------

    features["has_at_symbol"] = int(
        "@" in url
    )

    # ------------------------------------------------
    # 7. Subdomain count
    # ------------------------------------------------

    subdomain = extracted.subdomain

    if subdomain:
        features["subdomain_count"] = len(
            subdomain.split(".")
        )
    else:
        features["subdomain_count"] = 0

    # ------------------------------------------------
    # 8. Suspicious keywords
    # ------------------------------------------------

    suspicious_words = [
        "login",
        "verify",
        "verification",
        "account",
        "secure",
        "update",
        "password",
        "bank",
        "signin",
        "confirm",
        "free",
        "gift"
    ]

    url_lower = url.lower()

    features["suspicious_word_count"] = sum(
        word in url_lower
        for word in suspicious_words
    )

    return features


# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    test_url = "http://secure-login.example.com/verify/account"

    print("Testing URL:")
    print(test_url)

    print("\nExtracted Features:")
    print("-" * 40)

    features = extract_features(test_url)

    for name, value in features.items():
        print(f"{name}: {value}")