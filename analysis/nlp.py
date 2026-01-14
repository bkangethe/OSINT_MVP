classifier = None

def analyze_text(text, lang="en"):
    """
    Returns risk label and score for a given text.
    Supports Swahili, Sheng’, Somali phrases via multi-language model.
    """
    global classifier
    if classifier is None:
        from transformers import pipeline
        classifier = pipeline(
            "text-classification",
            model="joeddav/xlm-roberta-large-xnli"
        )
    try:
        results = classifier(text)
        label = results[0]["label"]
        score = float(results[0]["score"])
        if "CONTRADICTORY" in label or "EXTREME" in label:
            risk = "high"
        elif "NEUTRAL" in label:
            risk = "low"
        else:
            risk = "medium"
        return {"label": label, "score": score, "risk": risk}
    except Exception:
        return {"label": "unknown", "score": 0, "risk": "low"}
