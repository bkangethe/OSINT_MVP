NARRATIVE_KEYWORDS = {
    "political_unrest": ["protest", "riot", "government"],
    "hate_speech": ["hate", "enemy", "traitor"],
    "violence": ["kill", "attack", "weapon"]
}

def detect_narratives(texts):
    detected = {}

    for name, keywords in NARRATIVE_KEYWORDS.items():
        matches = []
        for text in texts:
            for word in keywords:
                if word in text.lower():
                    matches.append(word)

        if matches:
            detected[name] = list(set(matches))

    return detected
