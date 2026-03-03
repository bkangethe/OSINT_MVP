from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg

from .models import Alert



# SEVERITY CALCULATION


def calculate_severity(score: float, mention_count: int) -> str:
    

    if score >= 90 or mention_count >= 500:
        return "CRITICAL"
    elif score >= 70 or mention_count >= 250:
        return "HIGH"
    elif score >= 40 or mention_count >= 100:
        return "MEDIUM"
    return "LOW"



# COOLDOWN CHECK (Prevent Alert Spam)

def is_in_cooldown(cluster_id: str, minutes: int = 30) -> bool:
    

    cooldown_time = timezone.now() - timedelta(minutes=minutes)

    return Alert.objects.filter(
        cluster_id=cluster_id,
        created_at__gte=cooldown_time,
        status="ACTIVE"
    ).exists()



# BASELINE SPIKE DETECTION 


def exceeds_baseline(current_count: int, historical_counts: list, multiplier: float = 3.0) -> bool:
    

    if not historical_counts:
        return False

    baseline_avg = sum(historical_counts) / len(historical_counts)

    return current_count > (baseline_avg * multiplier)



# EMAIL SENDER


def send_alert_email(alert: Alert):
    
    subject = f" OSINT Alert - {alert.severity}"

    message = f"""
   
    OSINT NARRATIVE ALERT
    
    Title: {alert.title}

    Narrative Summary:
    {alert.narrative}

    Cluster ID: {alert.cluster_id}
    Mentions: {alert.mention_count}
    Risk Score: {alert.score}
    Severity: {alert.severity}
    Status: {alert.status}

    Time Detected: {alert.created_at}

   
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ALERT_EMAIL_RECIPIENT],  # set in settings.py
        fail_silently=False,
    )



# MAIN ALERT CREATOR FROM CLUSTER


def create_alert_from_cluster(cluster: dict):
   

    cluster_id = cluster.get("id")
    narrative_summary = cluster.get("summary")
    score = cluster.get("risk_score", 0)
    mention_count = cluster.get("size", 0)

    # 1️ Prevent duplicate active alerts
    existing = Alert.objects.filter(
        cluster_id=cluster_id,
        status="ACTIVE"
    ).first()

    if existing:
        return existing

    # 2️ Cooldown check
    if is_in_cooldown(cluster_id):
        return None

    # 3️ Calculate severity
    severity = calculate_severity(score, mention_count)

    # 4️ Create alert
    alert = Alert.objects.create(
        title=f"Narrative Surge Detected (Cluster {cluster_id})",
        narrative=narrative_summary,
        cluster_id=cluster_id,
        severity=severity,
        score=score,
        mention_count=mention_count,
    )

    # 5️ Send email
    send_alert_email(alert)

    return alert