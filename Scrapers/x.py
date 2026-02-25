import os
import logging
from typing import Any

import requests
from dotenv import load_dotenv

from api.models import RawJSONData

load_dotenv()
LOGGER = logging.getLogger(__name__)

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
BASE_URL = "https://api.twitter.com/2"
REQUEST_TIMEOUT = 15
TWITTER_MIN_RESULTS = 1
TWITTER_MAX_RESULTS = 2

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
}


def _normalize_max_results(max_results: int) -> int:
    if max_results <= 0:
        return TWITTER_MIN_RESULTS
    return max(TWITTER_MIN_RESULTS, min(TWITTER_MAX_RESULTS, max_results))


def get_user(username: str) -> dict[str, Any]:
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

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        return {"error": f"REQUEST_FAILED: {exc}"}

    if response.status_code != 200:
        return {"error": f"HTTP_{response.status_code}"}

    return response.json().get("data") or {}


def get_recent_tweets_by_user_id(user_id: str, max_results: int) -> dict[str, Any]:
    """
    Fetch recent tweets for a given user ID.
    """

    url = f"{BASE_URL}/users/{user_id}/tweets"
    params = {
        "max_results": _normalize_max_results(max_results),
        "tweet.fields": (
            "id,text,created_at,author_id,conversation_id,in_reply_to_user_id,"
            "lang,entities,attachments,context_annotations,geo,public_metrics,"
            "possibly_sensitive,referenced_tweets,reply_settings,source"
        ),
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url",
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"error": f"REQUEST_FAILED: {exc}"}

    return response.json()

def search_x(username: str, max_results: int = TWITTER_MIN_RESULTS) -> dict[str, Any]:
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
        results["error"] = "INVALID_USERNAME"
        return results

    user = get_user(username)
    if user:
        RawJSONData.objects.create(data=user)

    if not user or user.get("error"):
        results["error"] = user.get("error") if isinstance(user, dict) else "USER_LOOKUP_FAILED"
        return results

    results["people"].append(user)

    # -tweets
    try:
        tweets_response = get_recent_tweets_by_user_id(
            user_id=user["id"],
            max_results=max_results,
        )
        if tweets_response:
            RawJSONData.objects.create(data=tweets_response)

        if tweets_response.get("error"):
            results["error"] = tweets_response["error"]
            return results

        tweets = tweets_response.get("data", [])
        includes = tweets_response.get("includes", {})
        requested_count = max(0, max_results)
        for tweet in tweets[:requested_count]:
            text = tweet.get("text")

            tweet["includes"] = includes

            results["tweets"].append({
                "raw": tweet,
            })
            print(results)
        return results

    except (KeyError, TypeError, ValueError) as exc:
        LOGGER.exception("Error while processing tweets for username '%s'", username)
        results["error"] = str(exc)
        return results
