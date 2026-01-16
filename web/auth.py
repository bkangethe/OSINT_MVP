from flask import Blueprint, request, jsonify
from models import db, User
import jwt, datetime, os

auth_bp = Blueprint("auth", __name__)
SECRET = os.environ.get("SECRET_KEY", "dev")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error":"Missing credentials"}),400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error":"User exists"}),400

    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"User created"}),201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error":"Missing credentials"}),400

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error":"Invalid credentials"}),401

    token = jwt.encode({
        "user": user.username,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }, SECRET, algorithm="HS256")

    return jsonify({"token": token})
