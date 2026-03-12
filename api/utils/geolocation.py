from collections import Counter
import json
from api.models import RawJSONData

def extract_geo_mentions():
    posts = RawJSONData.objects.all()
    locations = []

    for p in posts:
        # Ensure p.data is a dict; if it's a JSON string, parse it
        try:
            data = json.loads(p.data) if isinstance(p.data, str) else p.data
        except (json.JSONDecodeError, TypeError):
            # Skip this post if JSON is invalid or p.data is not dict-like
            continue

        # Safely get location info
        location = data.get("geo") or data.get("location")

        if location:
            locations.append(location)

    # Count mentions per location
    location_counts = Counter(locations)

    # Prepare results
    results = [{"location": loc, "mentions": count} for loc, count in location_counts.items()]

    return results