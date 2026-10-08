import unittest

from app.app import app


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")

    def test_valid_prediction(self):
        response = self.client.post(
            "/api/predict",
            json={"url": "https://www.google.com"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        self.assertIn("prediction", data)
        self.assertIn("risk", data)
        self.assertIn("legitimate_probability", data)
        self.assertIn("phishing_probability", data)
        self.assertIn("explanation", data)

    def test_missing_url(self):
        response = self.client.post(
            "/api/predict",
            json={"something": "else"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "URL is required"
        )

    def test_empty_url(self):
        response = self.client.post(
            "/api/predict",
            json={"url": ""}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "URL is required"
        )

    def test_non_string_url(self):
        response = self.client.post(
            "/api/predict",
            json={"url": 12345}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "URL must be a string"
        )

    def test_oversized_url(self):
        oversized_url = "https://" + ("a" * 2041)

        response = self.client.post(
            "/api/predict",
            json={"url": oversized_url}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "URL is too long"
        )

    def test_invalid_url_format(self):
        response = self.client.post(
            "/api/predict",
            json={"url": "not-a-url"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Invalid URL format"
        )

    def test_incomplete_url(self):
        response = self.client.post(
            "/api/predict",
            json={"url": "http://"}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Invalid URL format"
        )

    def test_valid_https_url(self):
        response = self.client.post(
            "/api/predict",
            json={"url": "https://example.com"}
        )

        self.assertEqual(response.status_code, 200)

    def test_url_with_credentials(self):
        response = self.client.post(
            "/api/predict",
            json={"url": "https://user:password@example.com/login"}
        )

        self.assertEqual(response.status_code, 200)

    def test_security_headers(self):
        response = self.client.get("/ui")

        self.assertEqual(
            response.headers.get("X-Content-Type-Options"),
            "nosniff"
        )

        self.assertEqual(
            response.headers.get("X-Frame-Options"),
            "DENY"
        )

        self.assertEqual(
            response.headers.get("Referrer-Policy"),
            "no-referrer"
        )

        response.close()

        self.assertEqual(
            response.headers.get("X-Content-Type-Options"),
            "nosniff"
        )

        self.assertEqual(
            response.headers.get("X-Frame-Options"),
            "DENY"
        )

        self.assertEqual(
            response.headers.get("Referrer-Policy"),
            "no-referrer"
        )


if __name__ == "__main__":
    unittest.main()