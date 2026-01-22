from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM, AutoModelForSequenceClassification, pipeline

path = 'afri_trained_full'

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)

# Load model
model = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True,
                            id2label={0: "Normal", 1: "Hate", 2: "Abuse"},
                            label2id={"Normal":0, "Hate":1, "Abuse":2}
                            )


classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    return_all_scores=False
)

def analyze_text(text):
    """
    Classifies text into Normal, Hate, or Abuse
    """
    result = classifier(text)[0]

    label = result["label"]
    score = float(result["score"])

    # Risk mapping based on YOUR labels
    if label == "Hate":
        risk = "high"
    elif label == "Abuse":
        risk = "medium"
    else:
        risk = "low"

    return {
        "label": label,
        "score": round(score, 4),
        "risk": risk
    }

