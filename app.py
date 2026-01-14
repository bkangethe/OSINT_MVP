from flask import Flask, request, jsonify, send_from_directory
import asyncio
from osint import batch_lookup

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    names_text = data.get("usernames", "")
    names = [n.strip() for n in names_text.split(",") if n.strip()]
    if not names:
        return jsonify({"error": "No usernames provided"}), 400
    result = asyncio.run(batch_lookup(names))
    return jsonify(result)

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)
