import requests
from nlp import analyze_text
from dotenv import load_dotenv
import os

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

import requests

BASE_URL = "https://api.twitter.com/2"

def get_user(username):
    url = f"{BASE_URL}/users/by/username/{username}"
    params = {
        "user.fields": "description,public_metrics,verified,profile_image_url,created_at"
    }

    r = requests.get(url, headers=HEADERS, params=params)

    # if r.status_code == 404:
    #     return None  
    
    if r.status_code != 200:
        return {"error": "RATE_LIMIT"}
    
    return r.json()["data"]



def get_recent_tweets_by_user_id(user_id, max_results=10):
    url = f"{BASE_URL}/users/{user_id}/tweets"
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,attachments",
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url"
    }

    r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def search_x(username, max_results=20):
    results = {
        "keyword": username,
        "people": [],
        "tweets": [],
        "error": [],
    }

    user = get_user(username)
    if user.get("error"):
        return results

    results["people"].append(user)

    try:
        tweets_response = get_recent_tweets_by_user_id(user["id"], max_results)

        if not tweets_response.get("data"):
            return results
        
        tweets = tweets_response.get("data", [])

        for tweet in tweets:
            text = tweet.get("text")
            if text:
                tweet["analysis"] = analyze_text(text)

            results["tweets"].append({
                    "id": tweet.get("id"),
                    "text": tweet.get("text"),
                    "created_at": tweet.get("created_at"),
                    "public_metrics": tweet.get("public_metrics"),
                    "analysis": analyze_text(tweet["text"]) if tweet.get("text") else None
                })

        return results

    except Exception as e:
        results = {
            "keyword": username,
            "people": [],
            "tweets": [],
            "error": str(e),
        }
        return results
    
