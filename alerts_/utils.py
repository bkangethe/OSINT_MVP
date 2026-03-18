from django.core.mail import send_mail
from django.conf import settings
from .models import Alert


def create_narrative_alert(cluster_data):
    """
    Creates alert and sends email notification.
    """

    alert = Alert.objects.create(
        title=f"Narrative Surge Detected (Cluster {cluster_data['cluster_id']})",
        description=cluster_data["summary"],
        severity=cluster_data["severity"],
        cluster_id=str(cluster_data["cluster_id"]),
        cluster_size=cluster_data["size"],
        avg_risk=cluster_data["avg_risk"],
    )

    send_mail(
        subject=f"[{cluster_data['severity'].upper()}] Narrative Alert",
        message=f"""
Narrative Surge Detected

Cluster ID: {cluster_data['cluster_id']}
Cluster Size: {cluster_data['size']}
Average Risk: {cluster_data['avg_risk']}
Severity: {cluster_data['severity']}

Summary:
{cluster_data['summary']}
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=["bskangethe@gmail.com"],  
        fail_silently=False,
    )

    return alert