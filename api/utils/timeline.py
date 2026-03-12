from collections import defaultdict
from api.models import RawJSONData


def narrative_timeline(keyword):

    posts = RawJSONData.objects.filter(data__text__icontains=keyword)

    timeline = defaultdict(int)

    for post in posts:
        date = post.created_at.date()
        timeline[str(date)] += 1

    return dict(timeline)