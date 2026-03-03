# import requests
# import re

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#     "Accept-Language": "en-US,en;q=0.9",
# }

# INSTAGRAM_SEARCH_URL = "https://www.instagram.com/web/search/topsearch/"

# def search_instagram(query="t.o.u.c.h.e", limit=5):
#     """
#     Search Instagram for usernames matching a query.
#     Returns a list of profile dicts.
#     """

#     results = []

#     params = {
#         "query": query,
#         "context": "blended",
#         "include_reel": False,
#     }

#     try:
#         r = requests.get(
#             INSTAGRAM_SEARCH_URL,
#             headers=HEADERS,
#             params=params,
#             timeout=8
#         )

#         if r.status_code != 200:
#             return results

#         data = r.json()

#         users = data.get("users", [])
#         for item in users[:limit]:
#             user = item.get("user", {})

#             results.append({
#                 "username": user.get("username"),
#                 "full_name": user.get("full_name"),
#                 "url": f"https://www.instagram.com/{user.get('username')}/",
#                 "followers": user.get("follower_count"),
#                 "is_private": user.get("is_private"),
#                 "is_verified": user.get("is_verified"),
#                 "profile_image": user.get("profile_pic_url"),
#                 "source": "instagram_search"
#             })

#     except requests.RequestException:
#         pass

#     return results

# print(search_instagram())

import instaloader
from analysis.nlp import analyze_text

# L = instaloader.Instaloader()
# USERNAME = "to.uchee"
# PASSWORD = "Mwenyewe"

L = instaloader.Instaloader()

# try:
#     L.login(USERNAME, PASSWORD)
# except instaloader.exceptions.TwoFactorAuthRequiredException:
#     code = input("Enter 2FA code from Instagram: ")
#     L.two_factor_login(code)

# L.save_session_to_file(USERNAME)
# print("Session saved successfully")

def search_instagram(keyword):

    results = {
        "keyword":keyword,
        "profile":[],
        "posts":[],
        "error":[],
               }

    username = keyword

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        for post in profile.get_posts():
            results["posts"].append({
                "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
                "caption": post.caption,
                "analysis": analyze_text(post.caption) if post.caption else None,
                "likes": post.likes,
                "comments": post.comments,
                "date": post.date_utc.isoformat(),
                "is_video": post.is_video
            })

        results["profile"].append({
            "username": profile.username,
            "full_name": profile.full_name,
            "bio": profile.biography,
            "followers": profile.followers,
            "following": profile.followees,
            "is_verified": profile.is_verified,
            "profile_pic": profile.profile_pic_url
        })
        return results

    except Exception as e:
        results["error"].append({
            "text":str(e)
        })
        return results

