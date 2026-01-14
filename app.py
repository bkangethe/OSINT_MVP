from flask import Flask, request, jsonify, send_from_directory
from osint import run_osint
from vision import analyze_image
import os

app = Flask(__name__, static_folder="frontend", static_url_path="/frontend")

# API endpoint: OSINT analysis
@app.route("/check", methods=["POST"])
def check():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username required"}), 400

    results = run_osint(username)
    return jsonify(results)

# API endpoint: image analysis
@app.route("/vision", methods=["POST"])
def vision_check():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    image = request.files["image"]
    result = analyze_image(image)
    return jsonify(result)

# Serve frontend index.html
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Serve other frontend static files
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
