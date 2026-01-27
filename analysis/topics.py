from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def cluster_topics(profiles):
    texts = [p["content"] for p in profiles]

    if len(texts) < 2:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(texts)
    similarity = cosine_similarity(tfidf)

    clusters = []
    for i in range(len(profiles)):
        for j in range(i + 1, len(profiles)):
            if similarity[i][j] > 0.35:
                clusters.append({
                    "profile_1": profiles[i]["username"],
                    "profile_2": profiles[j]["username"],
                    "similarity": round(float(similarity[i][j]), 2)
                })

    return clusters
