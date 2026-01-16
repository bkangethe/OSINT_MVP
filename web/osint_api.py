from analysis.nlp import analyze_text
from analysis.llm_summary import generate_summary

PLATFORMS = {
    "github": "https://github.com/{}",
    "twitter": "https://twitter.com/{}",
    "instagram": "https://instagram.com/{}"
}

def basic_lookup(username):
    profiles = []

    for platform, url in PLATFORMS.items():
        profiles.append({
            "platform": platform,
            "username": username,
            "url": url.format(username),
            "nlp": analyze_text(username)
        })

    summary = generate_summary(profiles)

    return {
        "profiles": profiles,
        "summary": summary
    }
