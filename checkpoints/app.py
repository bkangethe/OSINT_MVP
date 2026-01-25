from flask import Flask, send_from_directory, request, jsonify
from models import db
from auth import auth_bp
from osint import basic_lookup
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, ".", "Frontend")

print(FRONTEND_DIR)
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///local.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

db.init_app(app)

with app.app_context():
    db.create_all()

# AUTH ROUTES
app.register_blueprint(auth_bp)

# FRONTEND
@app.route("/index")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# OSINT API
@app.route("/api/check", methods=["POST"])
def check_user():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "username missing"}), 400
    return jsonify(basic_lookup(username))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
