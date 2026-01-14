from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime
from models import db, User
import os

auth_bp = Blueprint("auth", __name__)
SECRET = os.environ.get("SECRET_KEY", "dev")

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json
    hashed = generate_password_hash(data["password"])
    user = User(email=data["email"], password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    }, SECRET, algorithm="HS256")

    return jsonify({"token": token})
