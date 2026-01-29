from flask import Flask, request, jsonify
from analysis.vision import run_vision
from llm_summary import summarize
from bot_detection import detect_bots
from graph import analyze_network

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    username = request.json.get("username")
    result = {}

    # Example calls
    result["vision"] = run_vision(username)
    result["nlp"] = summarize(username)
    result["network"] = analyze_network(username)
    result["bots"] = detect_bots(username)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
