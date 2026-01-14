from collections import defaultdict

graph = defaultdict(set)

def add_relationship(source, target):
    graph[source].add(target)

def influence_score(username):
    connections = len(graph[username])
    return min(connections / 10, 1.0)

def coordinated_activity(username):
    return len(graph[username]) > 10
