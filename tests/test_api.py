import unittest

from app.app import app


class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        app.config["TESTING"] = True

        cls.client = app.test_client()


    # =====================================================
    # Health Endpoint
    # =====================================================

    def test_health_endpoint(self):

        response = self.client.get(
            "/api/health"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.get_json()["status"],
            "healthy"
        )


    # =====================================================
    # Valid Prediction
    # =====================================================

    def test_valid_prediction(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": "https://www.google.com"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        data = response.get_json()

        self.assertIn(
            "prediction",
            data
        )

        self.assertIn(
            "risk",
            data
        )

        self.assertIn(
            "legitimate_probability",
            data
        )

        self.assertIn(
            "phishing_probability",
            data
        )

        self.assertIn(
            "explanation",
            data
        )


    # =====================================================
    # Missing URL
    # =====================================================

    def test_missing_url(self):

        response = self.client.post(
            "/api/predict",
            json={
                "something": "else"
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "URL is required"
        )


    # =====================================================
    # Empty URL
    # =====================================================

    def test_empty_url(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": ""
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "URL is required"
        )


    # =====================================================
    # Non-string URL
    # =====================================================

    def test_non_string_url(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": 12345
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "URL must be a string"
        )


    # =====================================================
    # Invalid URL Format
    # =====================================================

    def test_invalid_url_format(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": "not-a-url"
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Invalid URL format"
        )


    # =====================================================
    # Incomplete URL
    # =====================================================

    def test_incomplete_url(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": "http://"
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Invalid URL format"
        )


    # =====================================================
    # Valid HTTPS URL
    # =====================================================

    def test_valid_https_url(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": "https://example.com"
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )


    # =====================================================
    # URL With Credentials
    # =====================================================

    def test_url_with_credentials(self):

        response = self.client.post(
            "/api/predict",
            json={
                "url": (
                    "https://user:password@example.com/login"
                )
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )


    # =====================================================
    # Oversized URL
    # =====================================================

    def test_oversized_url(self):

        oversized_url = (
            "https://" +
            ("a" * 2041)
        )

        response = self.client.post(
            "/api/predict",
            json={
                "url": oversized_url
            }
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "URL is too long"
        )


    # =====================================================
    # Oversized Request Body
    # =====================================================

    def test_oversized_request_body(self):

        large_value = "A" * (17 * 1024)

        response = self.client.post(
            "/api/predict",
            json={
                "url": "https://example.com",
                "junk": large_value
            }
        )

        self.assertEqual(
            response.status_code,
            413
        )

        self.assertEqual(
            response.get_json()["error"],
            "Request body is too large"
        )


    # =====================================================
    # JSON Array Instead of Object
    # =====================================================

    def test_json_array_body(self):

        response = self.client.post(
            "/api/predict",
            json=[
                "https://example.com"
            ]
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Request body must be a JSON object"
        )


    # =====================================================
    # JSON String Instead of Object
    # =====================================================

    def test_json_string_body(self):

        response = self.client.post(
            "/api/predict",
            json="hello"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Request body must be a JSON object"
        )


    # =====================================================
    # JSON Number Instead of Object
    # =====================================================

    def test_json_number_body(self):

        response = self.client.post(
            "/api/predict",
            json=12345
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Request body must be a JSON object"
        )


    # =====================================================
    # Malformed JSON
    # =====================================================

    def test_malformed_json(self):

        response = self.client.post(
            "/api/predict",
            data='{"url":',
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Request body must be JSON"
        )


    # =====================================================
    # Wrong Content Type
    # =====================================================

    def test_wrong_content_type(self):

        response = self.client.post(
            "/api/predict",
            data='{"url":"https://example.com"}',
            content_type="text/plain"
        )

        self.assertEqual(
            response.status_code,
            400
        )

        self.assertEqual(
            response.get_json()["error"],
            "Request body must be JSON"
        )


    # =====================================================
    # GET Method Not Allowed
    # =====================================================

    def test_get_predict_not_allowed(self):

        response = self.client.get(
            "/api/predict"
        )

        self.assertEqual(
            response.status_code,
            405
        )


    # =====================================================
    # PUT Method Not Allowed
    # =====================================================

    def test_put_predict_not_allowed(self):

        response = self.client.put(
            "/api/predict",
            json={
                "url": "https://example.com"
            }
        )

        self.assertEqual(
            response.status_code,
            405
        )


    # =====================================================
    # Security Headers
    # =====================================================

    def test_security_headers(self):

        response = self.client.get(
            "/ui"
        )

        self.assertEqual(
            response.headers.get(
                "X-Content-Type-Options"
            ),
            "nosniff"
        )

        self.assertEqual(
            response.headers.get(
                "X-Frame-Options"
            ),
            "DENY"
        )

        self.assertEqual(
            response.headers.get(
                "Referrer-Policy"
            ),
            "no-referrer"
        )

        response.close()


# =========================================================
# Test Runner
# =========================================================

if __name__ == "__main__":

    unittest.main()