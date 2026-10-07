import re
import math
import tldextract

from urllib.parse import urlparse
from difflib import SequenceMatcher


# ---------------------------------------------------------
# Common brands frequently impersonated in phishing
# ---------------------------------------------------------

KNOWN_BRANDS = [
    "paypal",
    "google",
    "microsoft",
    "apple",
    "amazon",
    "facebook",
    "instagram",
    "linkedin",
    "github",
    "netflix",
]


# ---------------------------------------------------------
# Calculate Shannon entropy
# ---------------------------------------------------------

def calculate_entropy(text):

    if not text:
        return 0.0

    probabilities = []

    for character in set(text):
        probability = text.count(character) / len(text)
        probabilities.append(probability)

    entropy = 0

    for probability in probabilities:
        entropy -= probability * math.log2(probability)

    return entropy


# ---------------------------------------------------------
# Normalize common digit substitutions
# ---------------------------------------------------------

def normalize_domain(domain):

    substitutions = {
        "0": "o",
        "1": "l",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "8": "b",
        "9": "g",
    }

    normalized = domain.lower()

    for digit, letter in substitutions.items():
        normalized = normalized.replace(
            digit,
            letter
        )

    return normalized


# ---------------------------------------------------------
# Calculate similarity to known brands
# ---------------------------------------------------------

def calculate_brand_features(domain):

    normalized_domain = normalize_domain(domain)

    highest_similarity = 0.0
    exact_brand_match = 0

    for brand in KNOWN_BRANDS:

        # Exact match using the original domain
        if domain.lower() == brand:
            exact_brand_match = 1

        similarity = SequenceMatcher(
            None,
            normalized_domain,
            brand
        ).ratio()

        if similarity > highest_similarity:
            highest_similarity = similarity

    # A high similarity is more interesting when:
    # 1. The raw domain is NOT exactly the brand
    # 2. The domain contains digit substitution

    digit_substitution = int(
        any(
            digit in domain
            for digit in ["0", "1", "3", "4", "5", "7", "8", "9"]
        )
    )

    brand_lookalike_score = (
        highest_similarity
        * digit_substitution
        * (1 - exact_brand_match)
    )

    return (
        highest_similarity,
        exact_brand_match,
        brand_lookalike_score
    )
# ---------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------

def extract_features_v2(url):

    features = {}

    parsed = urlparse(url)

    extracted = tldextract.extract(url)

    hostname = parsed.hostname or ""

    domain = extracted.domain or ""

    suffix = extracted.suffix or ""

    path = parsed.path or ""

    query = parsed.query or ""

    fragment = parsed.fragment or ""

    # -----------------------------------------------------
    # Basic URL features
    # -----------------------------------------------------

    features["url_length"] = len(url)

    features["hostname_length"] = len(hostname)

    features["path_length"] = len(path)

    features["query_length"] = len(query)

    features["fragment_length"] = len(fragment)

    # -----------------------------------------------------
    # Character counts
    # -----------------------------------------------------

    features["dot_count"] = url.count(".")

    features["hyphen_count"] = url.count("-")

    features["underscore_count"] = url.count("_")

    features["slash_count"] = url.count("/")

    features["question_count"] = url.count("?")

    features["equal_count"] = url.count("=")

    features["at_count"] = url.count("@")

    features["ampersand_count"] = url.count("&")

    features["percent_count"] = url.count("%")

    # -----------------------------------------------------
    # Letters and digits
    # -----------------------------------------------------

    features["digit_count"] = sum(
        character.isdigit()
        for character in url
    )

    features["letter_count"] = sum(
        character.isalpha()
        for character in url
    )

    features["hostname_digit_count"] = sum(
        character.isdigit()
        for character in hostname
    )

    features["hostname_letter_count"] = sum(
        character.isalpha()
        for character in hostname
    )

    # -----------------------------------------------------
    # HTTPS
    # -----------------------------------------------------

    features["uses_https"] = int(
        parsed.scheme.lower() == "https"
    )

    # -----------------------------------------------------
    # IP address
    # -----------------------------------------------------

    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    features["has_ip"] = int(
        bool(re.match(ip_pattern, hostname))
    )

    # -----------------------------------------------------
    # @ symbol
    # -----------------------------------------------------

    features["has_at_symbol"] = int(
        "@" in url
    )

    # -----------------------------------------------------
    # Subdomains
    # -----------------------------------------------------

    subdomain = extracted.subdomain

    if subdomain:
        features["subdomain_count"] = len(
            subdomain.split(".")
        )
    else:
        features["subdomain_count"] = 0

    # -----------------------------------------------------
    # Domain features
    # -----------------------------------------------------

    features["domain_length"] = len(domain)

    features["domain_digit_count"] = sum(
        character.isdigit()
        for character in domain
    )

    features["domain_hyphen_count"] = domain.count("-")

    features["domain_entropy"] = calculate_entropy(
        domain
    )

    # -----------------------------------------------------
    # Path structure
    # -----------------------------------------------------

    features["path_depth"] = len(
        [
            part
            for part in path.split("/")
            if part
        ]
    )

    # -----------------------------------------------------
    # Obfuscation indicators
    # -----------------------------------------------------

    features["has_punycode"] = int(
        "xn--" in hostname.lower()
    )

    features["has_percent_encoding"] = int(
        "%" in url
    )

    # -----------------------------------------------------
    # Suspicious keywords
    # -----------------------------------------------------

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
        "gift",
        "wallet",
        "billing",
        "payment",
        "recover",
    ]

    url_lower = url.lower()

    features["suspicious_word_count"] = sum(
        word in url_lower
        for word in suspicious_words
    )

    # -----------------------------------------------------
    # Brand similarity
    # -----------------------------------------------------

    brand_similarity, exact_brand_match, brand_lookalike_score = (
        calculate_brand_features(domain)
    )

    features["brand_similarity"] = brand_similarity

    features["exact_brand_match"] = exact_brand_match

    features["brand_lookalike_score"] = brand_lookalike_score

    # -----------------------------------------------------
    # Digit substitution indicator
    # -----------------------------------------------------

    features["has_digit_substitution"] = int(
        any(
            digit in domain
            for digit in ["0", "1", "3", "4", "5", "7", "8", "9"]
        )
    )

    return features


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    test_urls = [
        "https://www.fakebook.com",
        "https://www.paypa1.com",
        "https://www.wifipedia.com",
        "https://www.google.com",
    ]

    for url in test_urls:

        print("\n" + "=" * 70)
        print(f"URL: {url}")
        print("=" * 70)

        features = extract_features_v2(url)

        for name, value in features.items():
            print(f"{name:30} : {value}")