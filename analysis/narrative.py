import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from datetime import datetime

class NarrativeClusterEngine:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Semantic vectorization
        """
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        """
        Convert list of texts into vector embeddings
        """
        return self.model.encode(texts, convert_to_numpy=True).astype(np.float32)

    def cluster(self, items, eps=0.35, min_samples=3):
        """
        Cluster a list of items (strings or dicts with "text").

        items: List[str] or List[dict] each with at least "text" key.
        eps: similarity threshold for DBSCAN (lower = stricter)
        min_samples: minimum cluster size

        Returns:
            clusters: List[dict] each representing a narrative cluster
        """
        if not items:
            return []

        # Normalize item
        normalized_items = []
        for item in items:
            if isinstance(item, str):
                normalized_items.append({"text": item, "timestamp": datetime.utcnow(), "risk_score": 0.0})
            elif isinstance(item, dict) and "text" in item:
                # Fill missing optional keys
                item.setdefault("timestamp", datetime.utcnow())
                item.setdefault("risk_score", 0.0)
                normalized_items.append(item)
            else:
                raise ValueError(f"Item must be str or dict with 'text', got {type(item)}")

        #  Extract texts and embed
        texts = [item["text"] for item in normalized_items]
        embeddings = self.embed(texts)

        # DBSCAN clustering
        clustering = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            metric="cosine"
        ).fit(embeddings)

        labels = clustering.labels_

        #  Organize clusters
        cluster_map = {}
        for idx, label in enumerate(labels):
            if label == -1:  # skip noise
                continue
            cluster_map.setdefault(int(label), []).append(normalized_items[idx])

        #  Format clusters for output
        clusters = []
        for cluster_id, posts in cluster_map.items():
            cluster_size = len(posts)
            avg_risk = np.mean([post.get("risk_score", 0.0) for post in posts])
            first_seen = min([post.get("timestamp", datetime.utcnow()) for post in posts])
            last_seen = max([post.get("timestamp", datetime.utcnow()) for post in posts])

            clusters.append({
                "cluster_id": cluster_id,
                "size": cluster_size,
                "avg_risk": round(float(avg_risk), 4),
                "first_seen": first_seen,
                "last_seen": last_seen,
                "posts": posts
            })

        return clusters
