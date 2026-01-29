KEYWORDS = {
    "violence": ["kill", "burn", "attack", "ua", "choma"],
    "extremism": ["jihad", "shabaab", "caliphate"],
    "hate": ["kafiri", "madoadoa"]
}

def analyze_text(text=""):
    text = text.lower()
    flags = [k for k,v in KEYWORDS.items() if any(w in text for w in v)]

    risk = "low"
    if "violence" in flags:
        risk = "high"
    elif flags:
        risk = "medium"

    return {"flags": flags, "risk": risk}
