from flask import Flask, send_from_directory, request, jsonify
from models import db
from auth import auth_bp
from osint import basic_lookup
import os, jwt

app = Flask(__name__, static_folder="Frontend", static_url_path="")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return send_from_directory("Frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("Frontend", path)

@app.route("/api/check", methods=["POST"])
def check():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(basic_lookup(request.json.get("username","")))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
