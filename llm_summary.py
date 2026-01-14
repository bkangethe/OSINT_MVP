from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(profile):
    text = f"""
    Username: {profile['name']}
    Bio: {profile['bio']}
    Risk Score: {profile['risk_score']}
    NLP Label: {profile['nlp']['label']}
    Network Influence: {profile['network_score']}
    """
    summary = summarizer(text, max_length=80, min_length=30, do_sample=False)[0]
    return summary["summary_text"]
