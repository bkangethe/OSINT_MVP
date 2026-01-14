from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from nlp import analyze_text
from scoring import calculate_risk
from graph import add_relationship, influence_score, coordinated_activity
from trends import detect_trends
from alerts import check_alerts
from llm_summary import generate_summary

model = SentenceTransformer("all-MiniLM-L6-v2")

# Simulated profiles for demonstration
SIMULATED_PROFILES = [
    {"name": "john_doe", "bio": "Tupigane na hawa watu. Serikali ni adui."},
    {"name": "kenya_voice", "bio": "Truth about elections must be shared."},
    {"name": "peace_254", "bio": "Promoting unity and peace in Kenya"}
]

def run_osint(username):
    results = []

    for profile in SIMULATED_PROFILES:
        bio = profile.get("bio", "")
        similarity = fuzz.partial_ratio(username.lower(), profile["name"].lower())

        nlp_result = analyze_text(bio)
        add_relationship(username, profile["name"])
        network_score = influence_score(username)
        risk_score = calculate_risk(
            nlp_result=nlp_result,
            similarity=similarity,
            network_score=network_score
        )

        summary = generate_summary({
            "name": profile["name"],
            "bio": bio,
            "risk_score": risk_score,
            "nlp": nlp_result,
            "network_score": network_score
        })

        results.append({
            "originalUsername": username,
            "name": profile["name"],
            "bio": bio,
            "similarity": similarity,
            "nlp": nlp_result,
            "network_score": round(network_score, 2),
            "risk_score": risk_score,
            "summary": summary
        })

    bios = [r["bio"] for r in results]
    trends = detect_trends(bios)
    alerts = check_alerts(results)

    return {
        "profiles": results,
        "trends": trends,
        "alerts": alerts
    }
