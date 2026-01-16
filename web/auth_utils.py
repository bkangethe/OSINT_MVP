from functools import wraps
from flask import request, jsonify
import jwt, os

SECRET = os.environ.get("SECRET_KEY", "dev")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error":"Missing or invalid Authorization header"}),401

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token expired"}),401
        except jwt.InvalidTokenError:
            return jsonify({"error":"Invalid token"}),401
        return f(*args, **kwargs)
    return decorated
