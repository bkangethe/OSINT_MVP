from flask import Blueprint, request, jsonify
from models import User, db
import jwt, os, hashlib

auth_bp = Blueprint("auth", __name__)

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json
    user = User(
        username=data["username"],
        password=hash_password(data["password"]),
        role=data.get("role", "viewer")
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "ok"}), 201

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if not user or user.password != hash_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "username": user.username,
        "role": user.role
    }, os.environ.get("SECRET_KEY", "dev"), algorithm="HS256")

    return jsonify({"token": token})