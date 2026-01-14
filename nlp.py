from langdetect import detect
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="facebook/roberta-hate-speech-dynabench-r4-target"
)

def analyze_text(text):
    if not text or len(text.strip()) < 5:
        return {
            "language": "unknown",
            "label": "NEUTRAL",
            "confidence": 0.0
        }

    try:
        language = detect(text)
    except:
        language = "unknown"

    result = classifier(text[:512])[0]

    return {
        "language": language,
        "label": result["label"],
        "confidence": round(result["score"], 2)
    }
