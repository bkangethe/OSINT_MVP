from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime, os
from models import db, User

auth_bp = Blueprint("auth", __name__)

SECRET = os.environ.get("SECRET_KEY", "dev")

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json
    user = User(
        username=data["username"],
        password=generate_password_hash(data["password"])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "registered"})

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }, SECRET, algorithm="HS256")

    return jsonify({"token": token})
