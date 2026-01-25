from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def detect_trends(texts):
    embeddings = model.encode(texts)
    avg = np.mean(embeddings, axis=0)
    trends = []

    for i, emb in enumerate(embeddings):
        similarity = np.dot(avg, emb) / (np.linalg.norm(avg) * np.linalg.norm(emb))
        if similarity > 0.75:
            trends.append(texts[i])

    return list(set(trends))
