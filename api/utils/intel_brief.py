from datetime import timedelta
from django.utils import timezone
from api.models import RawJSONData
from collections import Counter


def generate_daily_brief():

    today = timezone.now()
    yesterday = today - timedelta(hours=24)

    posts = RawJSONData.objects.filter(fetched_at__gte=yesterday)

    texts = [p.data.get("text", "") for p in posts]

    words = []

    for t in texts:
        words.extend(t.lower().split())

    top_narratives = Counter(words).most_common(10)

    report = {
        "total_posts": len(posts),
        "top_narratives": top_narratives
    }

    return report