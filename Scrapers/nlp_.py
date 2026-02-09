# nlp.py
from typing import Optional

PATH = "afri_trained_full"

_tokenizer = None
_model = None
_classifier = None
_sentiment_analyzer = None  # new


def get_classifier():
    """
    Lazily load tokenizer, model, and pipeline for classification.
    """
    global _tokenizer, _model, _classifier

    if _classifier is None:
        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

        _tokenizer = AutoTokenizer.from_pretrained(PATH, local_files_only=True)
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
            top_k=1,
        )

    return _classifier


def get_sentiment_analyzer():
    """
    Lazily load a Hugging Face sentiment analysis pipeline.
    """
    global _sentiment_analyzer

    if _sentiment_analyzer is None:
        from transformers import pipeline

        _sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        # You can pick another sentiment model if you prefer

    return _sentiment_analyzer


def analyze_text(text: str) -> dict:
    """
    Analyze the text for classification and sentiment, safely.
    Returns a dict with label, score, risk, sentiment, polarity, entities.
    """
    if not text or not text.strip():
        return {
            "label": "Normal",
            "score": 0.0,
            "risk": "low",
            "sentiment": "neutral",
            "polarity": 0.0,
            "entities": [],
        }

    # Default fallback
    label = "Normal"
    score = 0.0
    risk = "low"
    sentiment = "neutral"
    polarity = 0.0

    # --- Classification ---
    try:
        classifier = get_classifier()
        result_list = classifier(text)
        if result_list and isinstance(result_list, list) and isinstance(result_list[0], dict):
            result = result_list[0]
            label = result.get("label", "Normal")
            score = float(result.get("score", 0.0))

            if label == "Abuse":
                risk = "high"
            elif label == "Hate":
                risk = "medium"
            else:
                risk = "low"
    except Exception as e:
        print("Classifier error:", e)

    # --- Sentiment ---
    try:
        sentiment_analyzer = get_sentiment_analyzer()
        sentiment_result_list = sentiment_analyzer(text)
        if sentiment_result_list and isinstance(sentiment_result_list, list) and isinstance(sentiment_result_list[0], dict):
            sentiment_label = sentiment_result_list[0].get("label", "neutral").lower()

            if "negative" in sentiment_label or "1" in sentiment_label or "2" in sentiment_label:
                sentiment = "negative"
                polarity = -1.0
            elif "positive" in sentiment_label or "4" in sentiment_label or "5" in sentiment_label:
                sentiment = "positive"
                polarity = 1.0
            else:
                sentiment = "neutral"
                polarity = 0.0
    except Exception as e:
        print("Sentiment analyzer error:", e)

    return {
        "label": label,
        "score": round(score, 4),
        "risk": risk,
        "sentiment": sentiment,
        "polarity": polarity,
        "entities": [],
    }
