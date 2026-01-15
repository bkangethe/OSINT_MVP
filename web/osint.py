import requests
import os

def basic_lookup(username):
    """
    Sends a request to the worker service which runs ML/NLP/vision.
    Returns JSON results.
    """
    worker_url = os.environ.get("WORKER_URL")
    if not worker_url:
        return {"error": "WORKER_URL not set"}

    try:
        r = requests.post(f"{worker_url}/analyze", json={"username": username}, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}
