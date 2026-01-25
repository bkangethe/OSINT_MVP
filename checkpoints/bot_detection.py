def detect_bots(graph):
    bots = []
    for user, connections in graph.items():
        if len(connections) > 15:
            bots.append(user)
    return bots
