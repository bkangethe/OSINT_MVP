from flask import Flask, request, jsonify
from osint import run_osint
from vision import analyze_image

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username required"}), 400

    results = run_osint(username)
    return jsonify(results)

@app.route("/vision", methods=["POST"])
def vision_check():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    image = request.files["image"]
    result = analyze_image(image)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
