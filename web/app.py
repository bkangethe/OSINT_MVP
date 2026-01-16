from flask import Flask, render_template, request, jsonify
from models import db
from auth import auth_bp
from osint import basic_lookup
import os

app = Flask(__name__)

# CONFIG
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# AUTH
app.register_blueprint(auth_bp, url_prefix="/api/auth")

# FRONTEND
@app.route("/")
def index():
    return render_template("index.html")

# API
@app.route("/api/check", methods=["POST"])
def check_user():
    data = request.json or {}
    username = data.get("username")

    if not username:
        return jsonify({"error": "username missing"}), 400

    results = basic_lookup(username)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
