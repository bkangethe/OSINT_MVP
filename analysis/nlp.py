# nlp.py
from typing import Dict
from threading import Lock
from textblob import TextBlob  # For sentiment/polarity
import spacy  # For NER

PATH = "afri_trained_full"

_classifier = None
_lock = Lock()
MAX_INPUT_LENGTH = 2000

# Load spaCy once
_nlp_ner = spacy.load("en_core_web_sm")


def get_classifier():
    """Thread-safe lazy loading of HuggingFace classifier."""
    global _classifier
    if _classifier is None:
        with _lock:
            if _classifier is None:
                from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

                tokenizer = AutoTokenizer.from_pretrained(PATH, local_files_only=True)
                model = AutoModelForSequenceClassification.from_pretrained(PATH, local_files_only=True)

                # Ensure label mappings
                model.config.id2label = {0: "Normal", 1: "Hate", 2: "Abuse"}
                model.config.label2id = {"Normal": 0, "Hate": 1, "Abuse": 2}

                _classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=1)
    return _classifier


def analyze_text(text: str) -> Dict:
    """
    Analyze text for abuse/hate classification, sentiment, polarity, and entities.
    Returns JSON like:
    {
      "label": "Normal",
      "score": 0.8567,
      "risk": "low",
      "sentiment": "positive",
      "polarity": 0.72,
      "entities": [""]
    }
    """

    if not isinstance(text, str) or not text.strip():
        return {
            "label": None,
            "score": 0.0,
            "risk": None,
            "sentiment": None,
            "polarity": 0.0,
            "entities": [],
        }

    # Trim long input
    text = text.strip()[:MAX_INPUT_LENGTH]

    # --- Abuse/Hate classification ---
    classifier = get_classifier()
    try:
        raw_output = classifier(text)
        if isinstance(raw_output, list):
            first = raw_output[0]
            if isinstance(first, list):
                result = first[0]
            else:
                result = first
        else:
            result = raw_output

        label = result.get("label")
        score = float(result.get("score", 0.0))

    except Exception:
        label, score = None, 0.0

    # Risk mapping
    if label == "Abuse":
        risk = "high"
    elif label == "Hate":
        risk = "medium"
    else:
        risk = "low"

    # --- Sentiment analysis using TextBlob ---
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 2)
    if polarity > 0.05:
        sentiment = "positive"
    elif polarity < -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # --- Named Entity Recognition using spaCy ---
    doc = _nlp_ner(text)
    entities = [ent.text for ent in doc.ents]

    return {
        "label": label,
        "score": round(score, 4),
        "risk": risk,
        "sentiment": sentiment,
        "polarity": polarity,
        "entities": entities,
    }