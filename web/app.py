from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import jwt
import datetime
import os

app = Flask(__name__)
CORS(app)

# ===== CONFIG =====
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
app.config["SECRET_KEY"] = SECRET_KEY

# ===== MOCK USER (SAFE MVP) =====
USERS = {
    "brian": {
        "password": "admin123",
        "role": "analyst"
    }
}

# ===== ROUTES =====
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user = USERS.get(data.get("username"))

    if not user or user["password"] != data.get("password"):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "user": data["username"],
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=6)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"token": token})


@app.route("/api/check", methods=["POST"])
def osint_check():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except Exception:
        return jsonify({"error": "Invalid token"}), 401

    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"profiles": []})

    # SAFE MOCK RESULTS (NO SCRAPING)
    profiles = [
        {
            "platform": "twitter",
            "username": username,
            "url": f"https://twitter.com/{username}",
            "nlp": {"risk": "low"}
        },
        {
            "platform": "github",
            "username": username,
            "url": f"https://github.com/{username}",
            "nlp": {"risk": "low"}
        }
    ]

    return jsonify({"profiles": profiles})


if __name__ == "__main__":
    app.run(debug=True)
