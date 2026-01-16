from flask import Blueprint, request, jsonify
from auth_utils import token_required

check_bp = Blueprint("check", __name__)

@check_bp.route("/check", methods=["POST"])
@token_required
def check_username():
    data = request.json

    username = data.get("username")
    platform = data.get("platform", "all")

    if not username:
        return jsonify({"error": "Username required"}), 400

    # TEMP MOCK RESPONSE — confirms auth + frontend flow
    return jsonify({
        "profiles": [
            {
                "platform": "github",
                "username": username,
                "url": f"https://github.com/{username}",
                "nlp": {"risk": "low"}
            }
        ]
    })
