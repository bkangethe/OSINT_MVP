import requests
from .nlp_ import analyze_text
from dotenv import load_dotenv
import os

from api.models import RawJSONData

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

import requests

BASE_URL = "https://api.twitter.com/2"

def get_user(username):
    print(username)
    url = f"{BASE_URL}/users/by/username/{username}"
    params = {
        "user.fields": (
            "id,name,username,created_at,description,entities,location,"
            "profile_image_url,profile_banner_url,protected,public_metrics,"
            "verified,verified_followers_count,url,withheld,pinned_tweet_id,"
            "most_recent_tweet_id"
        )
    }

    r = requests.get(url, headers=HEADERS, params=params)
    print(r.status_code)

    if r.status_code != 200:
        return {"error": f"HTTP_{r.status_code}"}

    return r.json().get("data")

def get_recent_tweets_by_user_id(user_id, max_results):
    url = f"{BASE_URL}/users/{user_id}/tweets"
    params = {
        "max_results": max_results,
        "tweet.fields": (
            "id,text,created_at,author_id,conversation_id,in_reply_to_user_id,"
            "lang,entities,attachments,context_annotations,geo,public_metrics,"
            "possibly_sensitive,referenced_tweets,reply_settings,source"
            ),
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url"
    }

    r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def search_x(username, max_results=10):
    results = {
        "keyword": username,
        "people": [],
        "tweets": [],
        "error": [],
    }
    if len(username) < 3:
        print("Username too short")
        return results
    
    user = get_user(username)
    print(user)
    RawJSONData.objects.create(data=user)

    if user.get("error") or not user:
        return results

    results["people"].append(user)


    try:
        tweets_response = get_recent_tweets_by_user_id(user["id"], max_results)
        print(tweets_response)
        RawJSONData.objects.create(data=tweets_response)

        if not tweets_response.get("data"):
            return results
        
        tweets = tweets_response.get("data", [])
        for tweet in tweets:
            text = tweet.get("text")
            results["tweets"].append({
                "id": tweet.get("id"),
                "text": text,
                "created_at": tweet.get("created_at"),
                "public_metrics": tweet.get("public_metrics"),
                "analysis": analyze_text(text) if text else None
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
    

