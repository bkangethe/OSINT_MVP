from flask import Flask, send_from_directory, request, jsonify
from Backend.models import db
from Backend.auth import auth_bp
from Backend.osint import basic_lookup
import os

# Serve frontend and static files
app = Flask(__name__, static_folder="Frontend", static_url_path="")

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
db.init_app(app)

with app.app_context():
    db.create_all()

# AUTH ROUTES
app.register_blueprint(auth_bp)

# FRONTEND ROUTES
@app.route("/")
def serve_frontend():
    return send_from_directory("Frontend", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("Frontend", path)

# OSINT API
@app.route("/api/check", methods=["POST"])
def check_user():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "username missing"}), 400
    results = basic_lookup(username)
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
