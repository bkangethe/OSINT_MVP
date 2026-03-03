import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_summary(prompt_text):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text
    )
    return response.text