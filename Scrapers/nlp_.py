# nlp.py
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob

PATH = 'afri_trained_full'

tokenizer = AutoTokenizer.from_pretrained(PATH, local_files_only=True)

model = AutoModelForSequenceClassification.from_pretrained(
    PATH,
    local_files_only=True,
    id2label={0: "Normal", 1: "Hate", 2: "Abuse"},
    label2id={"Normal": 0, "Hate": 1, "Abuse": 2}
)

classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=False
)

def analyze_text(text: str) -> dict:
    if not text or text.strip() == "":
        return {
            "label": "Normal",
            "score": 0.0,
            "risk": "low",
            "sentiment": "neutral",
            "polarity": 0.0,
            "entities": []
        }

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


#, 'sentiment': 'neutral'

