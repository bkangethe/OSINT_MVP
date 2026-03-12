from collections import Counter
from datetime import timedelta
from django.utils import timezone
from api.models import RawJSONData


def calculate_risk_scores():

    now = timezone.now()
    window = now - timedelta(hours=6)

    posts = RawJSONData.objects.filter(created_at__gte=window)

    texts = [p.data.get("text", "").lower() for p in posts]

    words = []

    for t in texts:
        words.extend(t.split())

    counts = Counter(words)

    results = []

    for narrative, volume in counts.most_common(20):

        velocity_score = min(volume * 2, 40)
        volume_score = min(volume, 40)

        risk_score = velocity_score + volume_score

        if risk_score > 70:
            level = "HIGH"
        elif risk_score > 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        results.append({
            "narrative": narrative,
            "volume": volume,
            "risk_score": risk_score,
            "level": level
        })

    return results