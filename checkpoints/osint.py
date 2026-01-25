from analysis import nlp, graph, vision
from Scrapers import facebook, x as X_
from Scrapers.instagram import search_instagram
import requests

def basic_lookup(target):
    results = {"target": target, "checks": {}, "profiles": [],"posts": []}

    # Standard platforms
    sites = {
        "github": f"https://github.com/{target}",
        "twitter": f"https://twitter.com/{target}",
        "linkedin": f"https://linkedin.com/in/{target}"
    }

    for site, url in sites.items():
        try:
            r = requests.get(url, timeout=5)
            results["checks"][site] = r.status_code == 200
            if r.status_code == 200:
                results["profiles"].append({
                    "platform": site,
                    "username": target,
                    "url": url,
                    "nlp": nlp.analyze_text(f"Check {target} for risks"),
                    "vision": vision.detect_objects()
                })
        except:
            results["checks"][site] = False

    # Instagram multi-results
    ig_data = search_instagram(target)
    print(ig_data)

    if not bool(ig_data.get("error",[])):
        ig_profile = ig_data.get("profile")[0]
        results["profiles"].append({
            "platform": "instagram",
            "url":f'https://www.instagram.com/{ig_profile["username"]}',
            "username":ig_profile["full_name"],
            "bio":ig_profile["bio"],
            "followers":ig_profile["followers"],
            "following":ig_profile["following"]
        })

        for post in ig_data.get("posts"):
            caption = post.get("caption", "")
            results["posts"].append({
                "platform": "instagram",
                "url": post.get("post_url"),
                "text": caption,
                "likes": post.get("likes", 0),
                "comments": post.get("comments", 0),
                "date": post.get("date"),
                "is_video": post.get("is_video", False),
                "nlp": post.get("analysis")
            })


    # Optional: Graph analysis
    results["graph"] = graph.build_network([{"username": target}])
    

    # Facebook results
    fb_data = facebook.search_source_monitor(target)
    fb_profiles = fb_data.get("people",[])
    for p in fb_profiles:
        results["profiles"].append({
            "platform":"facebook",
            "username":p.get("name"),
            "url":p.get("url"),
            
        })

    # x ddata
    x_data = X_.search_x(target)

    if x_data and not x_data.get("error"):
        for person in x_data.get("people", []):
            username = person.get("username")
            if not username:
                continue

            results["profiles"].append({
                "platform": "x/twitter",
                "username": username,
                "display_name": person.get("name"),
                "url": f"https://twitter.com/{username}",
                "bio": person.get("description"),
                "verified": person.get("verified"),
                "created_at": person.get("created_at"),
                "followers": person.get("public_metrics", {}).get("followers_count"),
                "following": person.get("public_metrics", {}).get("following_count"),
                "tweets_count": person.get("public_metrics", {}).get("tweet_count"),
                "profile_image": person.get("profile_image_url"),
            })

        for tweet in x_data.get("tweets", []):
            results["posts"].append({
                "platform": "x/twitter",
                "post_type": "tweet",
                "url": f"https://twitter.com/i/web/status/{tweet.get('id')}",
                "text": tweet.get("text"),
                "date": tweet.get("created_at"),
                "metrics": tweet.get("public_metrics"),
                "nlp": tweet.get("analysis"),
                "risk": tweet.get("analysis", {}).get("risk"),
            })

    print(results)
    return results

