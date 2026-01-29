import os
import requests

LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_ENDPOINT = "https://api.openai.com/v1/chat/completions"

def generate_summary(profiles):
    if not LLM_API_KEY:
        return "LLM summary unavailable (API key not configured)."

    platforms = [p["platform"] for p in profiles]
    risks = [p["nlp"]["risk"] for p in profiles]

    prompt = f"""
You are an intelligence analyst.

Given this OSINT data:
Platforms: {platforms}
Risk levels: {risks}

Write a concise intelligence-style assessment.
Focus on risk, coordination, and notable absence of threats.
"""

    response = requests.post(
        LLM_ENDPOINT,
        headers={
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 120
        },
        timeout=10
    )

    return response.json()["choices"][0]["message"]["content"]
