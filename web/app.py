from flask import Flask, send_from_directory, request, jsonify
from models import db
from auth import auth_bp
from osint_api import basic_lookup
import os

# -----------------------------
# Initialize Flask app
# -----------------------------
app = Flask(__name__, static_folder="../Frontend", static_url_path="")

# -----------------------------
# Configure database
# -----------------------------
db_url = os.environ.get("DATABASE_URL")

if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    # Local fallback so app ALWAYS starts
    db_url = "sqlite:///local.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# -----------------------------
# Register authentication routes
# -----------------------------
app.register_blueprint(auth_bp)

# -----------------------------
# Serve frontend
# -----------------------------
@app.route("/")
def serve_frontend():
    return send_from_directory("../Frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../Frontend", path)

# -----------------------------
# OSINT API endpoint
# -----------------------------
@app.route("/api/check", methods=["POST"])
def check_user():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "username missing"}), 400

    # Call Worker API
    results = basic_lookup(username)
    return jsonify(results)

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
