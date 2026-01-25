def calculate_risk(nlp_result, similarity, network_score=0):
    score = 0

    if nlp_result["label"] in ["HATE", "EXTREMISM"]:
        score += 40 * nlp_result["confidence"]

    score += similarity * 0.3
    score += network_score * 30

    return min(round(score, 1), 100)
