def build_graph(username):
    # Dummy graph for demo (replace with real graph logic)
    nodes = [
        {"id": username, "risk": "high"},
        {"id": "related_profile_1", "risk": "low"},
        {"id": "related_profile_2", "risk": "low"}
    ]
    links = [
        {"source": username, "target": "related_profile_1"},
        {"source": username, "target": "related_profile_2"}
    ]
    return {"nodes": nodes, "links": links}
