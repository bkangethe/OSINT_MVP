import networkx as nx

def build_network(profiles):
    G = nx.Graph()
    for p in profiles:
        G.add_node(p["username"])
    return {"nodes": list(G.nodes), "edges": list(G.edges)}
