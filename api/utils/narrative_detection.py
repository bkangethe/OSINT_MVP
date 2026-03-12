# api/utils/narrative_detection.py
from collections import Counter
from datetime import datetime, timedelta
from api.models import RawJSONData

def detect_narrative_surges(hours=24, min_mentions=5):
    """
    Detect narrative surges in RawJSONData.

    Args:
        hours (int): Number of past hours to consider for recent posts.
        min_mentions (int): Minimum number of mentions in recent posts to consider a surge.

    Returns:
        List of dicts with 'location' and 'mentions' indicating surges.
    """
    # Calculate cutoff time
    recent_time = datetime.utcnow() - timedelta(hours=hours)

    # Filter posts based on fetched_at
    recent_posts = RawJSONData.objects.filter(fetched_at__gte=recent_time)

    # Collect all locations from recent posts
    locations = []
    for post in recent_posts:
        # Assuming your JSON data structure may contain 'geo' or 'location'
        location = post.data.get("geo") or post.data.get("location")
        if location:
            locations.append(location)

    # Count mentions per location
    location_counts = Counter(locations)

    # Keep only locations with mentions >= min_mentions
    surges = [
        {"location": loc, "mentions": count}
        for loc, count in location_counts.items()
        if count >= min_mentions
    ]

    # Sort surges by mentions descending
    surges.sort(key=lambda x: x["mentions"], reverse=True)

    return surges