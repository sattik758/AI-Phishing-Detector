from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from urllib.parse import urlparse

from app.predictor import predict_url


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_FOLDER = PROJECT_ROOT / "frontend"

def is_valid_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.netloc:
        return False

    return True

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"

    return response

@app.route("/ui")
def frontend():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/ui/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AI Phishing Detection API",
        "status": "running"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/api/predict", methods=["POST"])
def predict():

    # Check JSON body
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    # Get URL
    url = data.get("url")

    if not url:
        return jsonify({
            "error": "URL is required"
        }), 400

    # Basic validation
    if not isinstance(url, str):
        return jsonify({
            "error": "URL must be a string"
        }), 400

    url = url.strip()

    if not url:
        return jsonify({
            "error": "URL cannot be empty"
        }), 400

    if not is_valid_url(url):
        return jsonify({
            "error": "Invalid URL format"
        }), 400

    # Prevent extremely large input
    if len(url) > 2048:
        return jsonify({
            "error": "URL is too long"
        }), 400

    # Prediction
    try:
        result = predict_url(url)

        return jsonify(result)

    except Exception:
        return jsonify({
            "error": "Prediction failed",
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )