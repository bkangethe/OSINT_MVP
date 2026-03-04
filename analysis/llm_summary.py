from django.conf import settings
from google import genai

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_summary(text):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=text,
    )
    return response.text