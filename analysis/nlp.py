# nlp.py
from textblob import TextBlob
from typing import Optional

PATH = "afri_trained_full"

_tokenizer = None
_model = None
_classifier = None


def get_classifier():
    """
    Lazily load tokenizer, model, and pipeline.
    This MUST NOT run at import time.
    """
    global _tokenizer, _model, _classifier

    if _classifier is None:
        from transformers import (
            pipeline,
            AutoTokenizer,
            AutoModelForSequenceClassification,
        )

        _tokenizer = AutoTokenizer.from_pretrained(
            PATH,
            local_files_only=True,
        )

        _model = AutoModelForSequenceClassification.from_pretrained(
            PATH,
            local_files_only=True,
            id2label={0: "Normal", 1: "Hate", 2: "Abuse"},
            label2id={"Normal": 0, "Hate": 1, "Abuse": 2},
        )

        _classifier = pipeline(
            "text-classification",
            model=_model,
            tokenizer=_tokenizer,
            top_k=1,  # replaces return_all_scores=False
        )

    return _classifier


def analyze_text(text: str) -> dict:
    if not text or not text.strip():
        return {
            "label": "Normal",
            "score": 0.0,
            "risk": "low",
            "sentiment": "neutral",
            "polarity": 0.0,
            "entities": [],
        }

    classifier = get_classifier()

    result = classifier(text)[0]
    label = result["label"]
    score = float(result["score"])

    if label == "Abuse":
        risk = "high"
    elif label == "Hate":
        risk = "medium"
    else:
        risk = "low"

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.2:
        sentiment = "positive"
    elif polarity < -0.2:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "label": label,
        "score": round(score, 4),
        "risk": risk,
        "sentiment": sentiment,
    }

