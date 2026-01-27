def build_graph(profiles, topic_links):
    nodes = []
    edges = []

    for p in profiles:
        nodes.append({
            "id": p["username"],
            "platform": p["platform"]
        })

    for link in topic_links:
        edges.append({
            "source": link["profile_1"],
            "target": link["profile_2"],
            "weight": link["similarity"]
        })

    return {
        "nodes": nodes,
        "edges": edges
    }
