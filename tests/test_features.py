
import unittest

from src.feature_extraction_v2 import extract_features_v2


class TestFeatureExtraction(unittest.TestCase):

    def test_basic_url(self):
        url = "https://www.google.com"
        features = extract_features_v2(url)

        self.assertIsInstance(features, dict)
        self.assertGreater(features["url_length"], 0)
        self.assertEqual(features["uses_https"], 1)
        self.assertEqual(features["has_ip"], 0)

    def test_ip_based_url(self):
        url = "http://192.168.1.1/login"
        features = extract_features_v2(url)

        self.assertEqual(features["has_ip"], 1)
        self.assertEqual(features["uses_https"], 0)

    def test_invalid_ipv4_address(self):
        url = "https://999.999.999.999/login"
        features = extract_features_v2(url)

        self.assertEqual(features["has_ip"], 0)

    def test_feature_count(self):
        url = "https://www.google.com"
        features = extract_features_v2(url)

        self.assertEqual(len(features), 34)

    def test_suspicious_words(self):
        url = "https://example.com/login/verify/account"
        features = extract_features_v2(url)

        self.assertGreater(features["suspicious_word_count"], 0)

    def test_digit_substitution(self):
        url = "https://paypa1.com"
        features = extract_features_v2(url)

        self.assertEqual(features["has_digit_substitution"], 1)
        self.assertGreater(features["brand_similarity"], 0)

    def test_punycode_detection(self):
        url = "https://xn--example-9za.com"
        features = extract_features_v2(url)

        self.assertEqual(features["has_punycode"], 1)

    def test_percent_encoding(self):
        url = "https://example.com/%2Flogin"
        features = extract_features_v2(url)

        self.assertEqual(features["has_percent_encoding"], 1)


if __name__ == "__main__":
    unittest.main()
