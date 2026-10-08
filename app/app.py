from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from urllib.parse import urlparse

from app.predictor import predict_url


# =========================================================
# Project Paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FRONTEND_FOLDER = PROJECT_ROOT / "frontend"


# =========================================================
# Flask Application
# =========================================================

app = Flask(__name__)


# Maximum HTTP request body size: 16 KB
#
# The URL itself is separately limited to 2048 characters.
# This prevents unnecessarily large JSON request bodies.
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024


# =========================================================
# URL Validation
# =========================================================

def is_valid_url(url):
    """
    Validate basic URL syntax.

    The application accepts only HTTP and HTTPS URLs
    with a non-empty network location / hostname.
    """

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.netloc:
        return False

    return True


# =========================================================
# Security Headers
# =========================================================

@app.after_request
def add_security_headers(response):

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = "no-referrer"

    return response


# =========================================================
# Request Size Error
# =========================================================

@app.errorhandler(413)
def request_entity_too_large(error):

    return jsonify({
        "error": "Request body is too large"
    }), 413


# =========================================================
# Frontend
# =========================================================

@app.route("/ui")
def frontend():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


@app.route("/ui/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )


# =========================================================
# API Home
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "AI Phishing Detection API",
        "status": "running"
    })


# =========================================================
# Health Check
# =========================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy"
    })


# =========================================================
# Prediction API
# =========================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    # -----------------------------------------------------
    # Parse JSON body
    # -----------------------------------------------------

    data = request.get_json(silent=True)


    # Malformed JSON / body that cannot be parsed as JSON
    if data is None:

        return jsonify({
            "error": "Request body must be JSON"
        }), 400


    # -----------------------------------------------------
    # JSON body must be an object
    # -----------------------------------------------------

    if not isinstance(data, dict):

        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400


    # -----------------------------------------------------
    # URL required
    # -----------------------------------------------------

    url = data.get("url")


    if url is None:

        return jsonify({
            "error": "URL is required"
        }), 400


    # -----------------------------------------------------
    # URL must be a string
    # -----------------------------------------------------

    if not isinstance(url, str):

        return jsonify({
            "error": "URL must be a string"
        }), 400


    # -----------------------------------------------------
    # Remove surrounding whitespace
    # -----------------------------------------------------

    url = url.strip()


    # -----------------------------------------------------
    # Empty URL
    # -----------------------------------------------------

    if not url:

        return jsonify({
            "error": "URL is required"
        }), 400


    # -----------------------------------------------------
    # URL syntax validation
    # -----------------------------------------------------

    if not is_valid_url(url):

        return jsonify({
            "error": "Invalid URL format"
        }), 400


    # -----------------------------------------------------
    # URL length validation
    # -----------------------------------------------------

    if len(url) > 2048:

        return jsonify({
            "error": "URL is too long"
        }), 400


    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    try:

        result = predict_url(url)

        return jsonify(result)


    except Exception:

        # Do not expose internal model/server errors
        # to the API client.

        return jsonify({
            "error": "Prediction failed"
        }), 500


# =========================================================
# Application Entry Point
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )