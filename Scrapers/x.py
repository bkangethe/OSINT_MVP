import os
import requests
from dotenv import load_dotenv

from api.models import RawJSONData
from .nlp_ import analyze_text

load_dotenv()

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
BASE_URL = "https://api.twitter.com/2"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
}

def get_user(username: str) -> dict | None:
    """
    Fetch a Twitter/X user by username.
    """
    url = f"{BASE_URL}/users/by/username/{username}"
    params = {
        "user.fields": (
            "id,name,username,created_at,description,entities,location,"
            "profile_image_url,profile_banner_url,protected,public_metrics,"
            "verified,verified_followers_count,url,withheld,pinned_tweet_id,"
            "most_recent_tweet_id"
        )
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return {"error": f"HTTP_{response.status_code}"}

    return response.json().get("data")


def get_recent_tweets_by_user_id(user_id: str, max_results: int) -> dict:
    """
    Fetch recent tweets for a given user ID.
    """
    url = f"{BASE_URL}/users/{user_id}/tweets"
    params = {
        "max_results": max_results,
        "tweet.fields": (
            "id,text,created_at,author_id,conversation_id,in_reply_to_user_id,"
            "lang,entities,attachments,context_annotations,geo,public_metrics,"
            "possibly_sensitive,referenced_tweets,reply_settings,source"
        ),
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url",
    }

    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()

    return response.json()

def search_x(username: str, max_results: int = 10) -> dict:
    """
    Search X/Twitter for a user and their recent tweets.
    Returns raw tweet data + NLP analysis.
    """
    results = {
        "keyword": username,
        "people": [],
        "tweets": [],
        "error": None,
    }

    if not username or len(username) < 3:
        return results

    # ---- Fetch user ----
    user = get_user(username)
    RawJSONData.objects.create(data=user)

    if not user or user.get("error"):
        return results

    results["people"].append(user)

    # -tweets
    try:
        tweets_response = get_recent_tweets_by_user_id(
            user_id=user["id"],
            max_results=max_results,
        )
        RawJSONData.objects.create(data=tweets_response)

        tweets = tweets_response.get("data", [])
        includes = tweets_response.get("includes", {})

        for tweet in tweets:
            text = tweet.get("text")

            tweet["includes"] = includes

            results["tweets"].append({
                "raw": tweet,
                "analysis": analyze_text(text) if text else None,
            })

        return results

    except Exception as exc:
        results["error"] = str(exc)
        return results
