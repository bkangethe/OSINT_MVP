# graph.py

import networkx as nx
from textblob import TextBlob
from collections import Counter

class Graph:
    def __init__(self, tweets):
        self.G = nx.DiGraph()
        self.tweets = tweets

    def create(self):
        for tweet in self.tweets:
            user = tweet.get("username")
            if not user:
                continue

            if not self.G.has_node(user):
                self.G.add_node(user,
                                tweet_count=0,
                                hashtags=set(),
                                urls=set(),
                                mentions=set(),
                                sentiments=[])

            self.G.nodes[user]["tweet_count"] += 1

            entities = tweet.get("entities", {})

            try:
                hashtags = {h.get("tag") for h in entities.get("hashtags", []) if h.get("tag")}
            except Exception:
                continue

            urls = {u.get("expanded_url") for u in entities.get("urls", []) if u.get("expanded_url")}
            mentions = {m.get("username") for m in entities.get("mentions", []) if m.get("username")}

            

            self.G.nodes[user]["hashtags"].update(hashtags)
            self.G.nodes[user]["urls"].update(urls)
            self.G.nodes[user]["mentions"].update(mentions)

            # Sentiment
            text = tweet.get("text", "")
            try:
                sentiment = TextBlob(text).sentiment
                self.G.nodes[user]["sentiments"].append({
                    "polarity": sentiment.polarity,
                    "subjectivity": sentiment.subjectivity
                })
            except Exception:
                self.G.nodes[user]["sentiments"].append({"polarity": None, "subjectivity": None})

            # Edges
            for mentioned_user in mentions:
                if mentioned_user == user:
                    continue
                if self.G.has_edge(user, mentioned_user):
                    self.G[user][mentioned_user]["weight"] += 1
                else:
                    self.G.add_edge(user, mentioned_user, weight=1)

        return self.G

    def extract_global_stats(self):
        hashtags = Counter()
        mentions = Counter()
        sentiments = []

        for node, data in self.G.nodes(data=True):
            hashtags.update(data.get("hashtags", []))
            mentions.update(data.get("mentions", []))
            sentiments.extend([s for s in data.get("sentiments", []) if s["polarity"] is not None])

        avg_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments) if sentiments else 0
        avg_subjectivity = sum(s['subjectivity'] for s in sentiments) / len(sentiments) if sentiments else 0

        return {
            "top_hashtags": hashtags.most_common(10),
            "top_mentions": mentions.most_common(10),
            "average_sentiment": {"polarity": avg_polarity, "subjectivity": avg_subjectivity}
        }

    def compute_metrics(self):
        metrics = {}
        metrics["degree"] = dict(self.G.degree(weight='weight'))
        metrics["in_degree"] = dict(self.G.in_degree(weight='weight'))
        metrics["out_degree"] = dict(self.G.out_degree(weight='weight'))
        metrics["betweenness"] = nx.betweenness_centrality(self.G, weight='weight', normalized=True)
        metrics["closeness"] = nx.closeness_centrality(self.G)
        try:
            metrics["eigenvector"] = nx.eigenvector_centrality_numpy(self.G, weight='weight')
        except nx.NetworkXException:
            metrics["eigenvector"] = {}

        metrics["density"] = nx.density(self.G)
        degrees = [deg for node, deg in self.G.degree()]
        metrics["average_degree"] = sum(degrees) / len(degrees) if degrees else 0

        # Central nodes
        metrics["central_nodes"] = {
            "degree": max(metrics["degree"], key=metrics["degree"].get, default=None),
            "in_degree": max(metrics["in_degree"], key=metrics["in_degree"].get, default=None),
            "out_degree": max(metrics["out_degree"], key=metrics["out_degree"].get, default=None),
            "betweenness": max(metrics["betweenness"], key=metrics["betweenness"].get, default=None),
            "closeness": max(metrics["closeness"], key=metrics["closeness"].get, default=None),
            "eigenvector": max(metrics.get("eigenvector", {}), key=metrics.get("eigenvector", {}).get, default=None)
        }

        return metrics

    def to_dict(self):
        """Return JSON-serializable graph including nodes, edges, global stats, and metrics"""
        nodes = [
            {
                "id": n,
                "tweet_count": d.get("tweet_count", 0),
                "hashtags": list(d.get("hashtags", [])),
                "urls": list(d.get("urls", [])),
                "mentions": list(d.get("mentions", [])),
                # "sentiments": d.get("sentiments", [])
            } for n, d in self.G.nodes(data=True)
        ]
        edges = [
            {"source": u, "target": v, "weight": d["weight"]}
            for u, v, d in self.G.edges(data=True)
        ]
        global_stats = self.extract_global_stats()
        metrics = self.compute_metrics()

        return {
            "nodes": nodes,
            "edges": edges,
            "global_stats": global_stats,
            "network_metrics": metrics
        }