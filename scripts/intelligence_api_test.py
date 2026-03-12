# intelligence_api_test.py
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Define all endpoints
endpoints = {
    "X Search": {"method": "GET", "url": f"{BASE_URL}/x-search?query=test&limit=5"},
    "Facebook Monitor": {"method": "GET", "url": f"{BASE_URL}/facebook-monitor?limit=5"},
    "Instagram Monitor": {"method": "GET", "url": f"{BASE_URL}/instagram-monitor?limit=5"},
    "NLP Analysis": {"method": "POST", "url": f"{BASE_URL}/nlp-analysis", "data": {"text": "Sample text for NLP analysis."}},
    "Graph Analysis": {"method": "GET", "url": f"{BASE_URL}/graph"},
    "Narrative Clustering": {"method": "GET", "url": f"{BASE_URL}/narratives/clusters/"},
    "Narrative Surges": {"method": "GET", "url": f"{BASE_URL}/narratives/surges/"},
    "Narrative Timeline": {"method": "GET", "url": f"{BASE_URL}/narratives/timeline/?format=json"},
    "Geo Mentions": {"method": "GET", "url": f"{BASE_URL}/narratives/geo/"},
    "Intelligence Brief": {"method": "GET", "url": f"{BASE_URL}/intel/brief/?format=json"},
    "AI Summary": {"method": "POST", "url": f"{BASE_URL}/summary", "data": {"text": "This is a sample intelligence text to summarize."}},
    "Data Check": {"method": "GET", "url": f"{BASE_URL}/check"},
    "Telegram Scrape": {"method": "GET", "url": f"{BASE_URL}/telegram-scrape?channels=bnnkenya,cnn&limit=5"}
}

def call_endpoint(name, info):
    try:
        if info["method"] == "GET":
            response = requests.get(info["url"])
        elif info["method"] == "POST":
            response = requests.post(info["url"], json=info.get("data", {}))
        else:
            print(f"[{name}] Unsupported method: {info['method']}")
            return

        print(f"\n--- {name} ---")
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(response.text)
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception calling {name}: {e}")

if __name__ == "__main__":
    for name, info in endpoints.items():
        call_endpoint(name, info)