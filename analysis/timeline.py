from collections import Counter
from datetime import datetime

def analyze_timeline(posts):
    timeline = Counter()

    for post in posts:
        date = post.get("date")
        if not date:
            continue

        day = datetime.strptime(date, "%Y-%m-%d").date()
        timeline[str(day)] += 1

    trend = "stable"
    if len(timeline) >= 2:
        values = list(timeline.values())
        if values[-1] > values[0] * 1.5:
            trend = "increasing"
        elif values[-1] < values[0] * 0.5:
            trend = "decreasing"

    return {
        "activity_by_day": timeline,
        "trend": trend
    }