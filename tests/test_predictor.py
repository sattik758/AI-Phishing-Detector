import unittest

from app.predictor import predict_url


class TestPredictor(unittest.TestCase):

    def test_legitimate_url(self):
        result = predict_url("https://www.google.com")

        self.assertIn(result["prediction"], ["LEGITIMATE", "PHISHING"])
        self.assertGreaterEqual(result["legitimate_probability"], 0)
        self.assertLessEqual(result["legitimate_probability"], 1)
        self.assertGreaterEqual(result["phishing_probability"], 0)
        self.assertLessEqual(result["phishing_probability"], 1)

    def test_phishing_test_url(self):
        result = predict_url("https://paypa1.com")

        self.assertEqual(result["prediction"], "PHISHING")
        self.assertGreater(result["phishing_probability"], 0.5)

    def test_result_structure(self):
        result = predict_url("https://example.com")

        required_keys = {
            "url",
            "prediction",
            "legitimate_probability",
            "phishing_probability",
            "risk",
            "explanation"
        }

        self.assertTrue(required_keys.issubset(result.keys()))

    def test_risk_level(self):
        result = predict_url("https://www.google.com")

        self.assertIn(
            result["risk"],
            ["LOW", "MEDIUM", "HIGH"]
        )

    def test_explanation(self):
        result = predict_url("https://paypa1.com")

        self.assertIsInstance(result["explanation"], list)
        self.assertGreater(len(result["explanation"]), 0)


if __name__ == "__main__":
    unittest.main()