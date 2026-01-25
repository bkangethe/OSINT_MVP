import requests
import time
from datetime import datetime
# from .nlp_ import analyze_text

BASE_URL = "https://facebook-scraper3.p.rapidapi.com/"
DELAY = 1.5

# params = {
#     'query':query,
#     'limit':10,
# }


HEADERS = {
    "x-rapidapi-key": "eea74e68d1mshf4a21f8613f8753p14149cjsndc45f1c1a65c",
    "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
}



def search_pages(keyword, max_pages=5):
    """Search Pages for a keyword, return list of dicts with page info"""
    url = f"{BASE_URL}/search/pages"
    all_pages = []
    cursor = None

    for _ in range(max_pages):
        params = {"query": keyword}
        if cursor:
            params["cursor"] = cursor

        resp = requests.get(url, headers=HEADERS, params=params)
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break

        for item in results:
            all_pages.append({
                "facebook_id": item.get("facebook_id"),
                "name": item.get("name"),
                "profile_url": item.get("profile_url"),
                "type": item.get("type"),
                "is_verified": item.get("is_verified", False),
                "image_url": item.get("image", {}).get("uri")
            })

        cursor = data.get("cursor")
        time.sleep(DELAY)

    return all_pages

def fetch_posts(page_id, max_posts=10):
    """Fetch posts from a page"""
    url = f"{BASE_URL}/get/page"
    params = {"page_id": page_id, "limit": max_posts}
    resp = requests.get(url, headers=HEADERS, params=params)
    data = resp.json()
    posts = []
    for p in data.get("posts", []):
        posts.append({
            "post_id": p.get("post_id"),
            "text": p.get("text"),
            "created_time": p.get("created_time"),
            "url": p.get("url"),
            "image": p.get("image")
        })
    
    return posts

def fetch_comments(post_id, max_comments=10):
    """Fetch comments for a post"""
    url = f"{BASE_URL}/get/post/comments"
    params = {"post_id": post_id, "limit": max_comments}
    resp = requests.get(url, headers=HEADERS, params=params)
    data = resp.json()
    comments = []
    for c in data.get("comments", []):
        comments.append({
            "comment_id": c.get("comment_id"),
            "text": c.get("text"),
            "created_time": c.get("created_time"),
            "user_name": c.get("user_name"),
            "user_id": c.get("user_id")
        })
    return comments

def fetch_people(name):
    """Fetch usernames + profile"""
    url = f"{BASE_URL}/search/people"
    params = {'query': name}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp_json = resp.json()
    resp_json = resp_json.get("results",[])

    profiles = []
    for resp in resp_json:
        profiles.append(
            {
                "profileID":resp.get("profile_id"),
                "name":resp.get("name"),
                "url":resp.get("url")
            }
        )
    return profiles

def search_source_monitor(keyword):
    data = {
            "keyword": "Shem",
            "scraped_at": "2026-01-15T12:34:56.123456",
            "people": [
                {
                    "profileID": "100087654321",
                    "name": "Shem Otieno",
                    "url": "https://www.facebook.com/profile.php?id=100087654321"
                },
                {
                    "profileID": "100012345678",
                    "name": "Shem Mwangi",
                    "url": "https://www.facebook.com/profile.php?id=100012345678"
                }
            ],
            "pages": [
                {
                    "facebook_id": "1234567890",
                    "name": "Shem Official",
                    "profile_url": "https://www.facebook.com/ShemOfficial",
                    "type": "Public Figure",
                    "is_verified": True,
                    "image_url": "https://scontent.xx.fbcdn.net/page.jpg",
                    "posts": [
                        {
                            "post_id": "pfbid02ABC",
                            "text": "Shem will be speaking at the conference today.",
                            "created_time": "2026-01-10T09:15:22",
                            "url": "https://www.facebook.com/ShemOfficial/posts/pfbid02ABC",
                            "image": "https://scontent.xx.fbcdn.net/post.jpg",
                            "comments": [
                                {
                                    "comment_id": "cmt123",
                                    "text": "Looking forward to seeing Shem!",
                                    "text_analysis": "",
                                    "created_time": "2026-01-10T10:01:11",
                                    "user_name": "John Doe",
                                    "user_id": "99887766"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

    return data
    """
    Fetch all Facebook data related to a keyword in one unified dataset.
    Includes pages, posts, comments, and optionally people profiles.
    """
    result_dict = {
        "keyword": keyword,
        "people": [],
        "pages": []
    }


    result_dict["people"] = fetch_people(keyword)

    pages = search_pages(keyword)
    for page in pages:
        page_entry = page.copy()

        posts = fetch_posts(page["facebook_id"])
        filtered_posts = []

        for post in posts:
            if post["text"] and keyword.lower() in post["text"].lower():
                post_entry = post.copy()

                # 4. Fetch comments for each post
                comments = fetch_comments(post["post_id"])
                filtered_comments = [
                    c for c in comments if c["text"] and keyword.lower() in c["text"].lower()
                ]
                post_entry["comments"] = filtered_comments
                filtered_posts.append(post_entry)

        page_entry["posts"] = filtered_posts
        result_dict["pages"].append(page_entry)
        print(result_dict)
    return result_dict

