KEYWORD_RISK = {
    "attack": 3,
    "kill": 3,
    "riot": 2,
    "protest": 2,
    "bomb": 3,
    "hate": 2,
    "weapon": 3
}

def assess_threat(texts):
    score = 0
    matched = []

    for text in texts:
        lower = text.lower()
        for word, weight in KEYWORD_RISK.items():
            if word in lower:
                score += weight
                matched.append(word)

    if score >= 6:
        level = "high"
    elif score >= 3:
        level = "medium"
    else:
        level = "low"

    return {
        "level": level,
        "score": score,
        "keywords": list(set(matched))
    }
