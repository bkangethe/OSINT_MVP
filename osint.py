import asyncio
import aiohttp
from aiohttp import ClientTimeout, ClientError
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import re

# Platforms
PLATFORMS = {
    "github": "direct:https://github.com/{username}",
    "twitter": "direct:https://twitter.com/{username}",
    "instagram": "instagram.com",  # Use search fallback
    "linkedin": "linkedin.com/in",
    "facebook": "facebook.com"
}

def is_valid_username(username):
    return bool(username) and bool(re.fullmatch(r"[A-Za-z0-9._-]+", username))

async def check_direct(session, url, retries=2):
    for attempt in range(retries+1):
        try:
            async with session.get(url, timeout=ClientTimeout(total=10)) as resp:
                return url if resp.status < 400 else None
        except ClientError:
            if attempt < retries:
                await asyncio.sleep(1)
                continue
            return None

async def google_search_multi(session, site, name, max_results=5):
    """Search Google for multiple profiles on a platform"""
    query = f"site:{site} {name}"
    url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    candidates = []

    try:
        async with session.get(url, headers=headers, timeout=ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return []
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            links = [a['href'] for a in soup.find_all('a', href=True)]
            for link in links:
                if site in link and len(candidates) < max_results:
                    profile_name = link.split("/")[-1].replace("-", " ").title()
                    similarity = fuzz.ratio(name.lower(), profile_name.lower())
                    candidates.append({
                        "name": profile_name,
                        "url": link,
                        "similarity": similarity,
                        "profile_pic": "",  # to be fetched
                        "location": ""      # to be fetched
                    })
        return candidates
    except ClientError:
        return []

async def fetch_profile_details(session, url, platform):
    """Fetch profile pic and location/bio if possible"""
    profile_pic = ""
    location = ""
    try:
        async with session.get(url, timeout=ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                return profile_pic, location
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            
            if platform in ["github", "twitter"]:
                img_tag = soup.find("img", {"alt": "Avatar"}) or soup.find("img", {"class": "avatar-user"})
                if img_tag:
                    profile_pic = img_tag.get("src", "")
            elif platform in ["linkedin", "instagram"]:
                meta_img = soup.find("meta", {"property":"og:image"})
                if meta_img:
                    profile_pic = meta_img.get("content", "")
                meta_desc = soup.find("meta", {"name":"description"})
                if meta_desc:
                    location = meta_desc.get("content", "")
    except:
        pass
    return profile_pic, location

async def check_platform(session, platform, template, name):
    if template.startswith("direct:"):
        url = template.replace("direct:", "").format(username=name)
        result = await check_direct(session, url)
        if result:
            profile_pic, location = await fetch_profile_details(session, result, platform)
            return platform, [{
                "name": name,
                "url": result,
                "similarity": 100,
                "profile_pic": profile_pic,
                "location": location
            }]
        return platform, []
    else:
        candidates = await google_search_multi(session, template, name)
        detailed_candidates = []
        for c in candidates:
            pic, loc = await fetch_profile_details(session, c["url"], platform)
            c["profile_pic"] = pic
            c["location"] = loc
            detailed_candidates.append(c)
        return platform, detailed_candidates

async def check_username(name):
    results = {"target": name, "checks": {}}
    async with aiohttp.ClientSession() as session:
        tasks = []
        for platform, template in PLATFORMS.items():
            tasks.append(asyncio.create_task(check_platform(session, platform, template, name)))

        for future in asyncio.as_completed(tasks):
            platform, candidates = await future
            results["checks"][platform] = candidates
    return results

async def batch_lookup(names):
    all_results = []
    for name in names:
        result = await check_username(name)
        all_results.append(result)
    return all_results
