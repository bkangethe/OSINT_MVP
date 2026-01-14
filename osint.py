from analysis import nlp, graph, vision
from scrapers import instagram
import requests

def basic_lookup(target):
    results = {"target": target, "checks": {}, "profiles": []}

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
    ig_profiles = instagram.search_instagram(target)
    for p in ig_profiles:
        results["profiles"].append({
            "platform": "instagram",
            **p,
            "nlp": nlp.analyze_text(f"Check {p['username']} for risks"),
            "vision": vision.detect_objects()
        })

    # Optional: Graph analysis
    results["graph"] = graph.build_network([{"username": target}])

    return results
