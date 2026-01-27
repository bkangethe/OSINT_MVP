@app.route("/api/check", methods=["POST"])
def check_user():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "username missing"}), 400

    profiles = basic_lookup(username)
    texts = [p.get("bio", "") for p in profiles]

    threat = assess_threat(texts)
    topics = extract_topics(texts)
    narratives = detect_narratives(topics, threat)
    timeline = build_timeline(profiles)
    graph = build_graph(username, profiles, topics)

    return jsonify({
        "username": username,
        "profiles": profiles,
        "threat": threat,
        "topics": topics,
        "narratives": narratives,
        "timeline": timeline,
        "graph": graph
    })
