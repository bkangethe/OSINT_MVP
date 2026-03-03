from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Alert


@api_view(["GET"])
def alert_history(request):
    """
    Get all alerts (Alert History)
    """
    alerts = Alert.objects.all().order_by("-created_at")

    data = [
        {
            "id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity,
            "cluster_size": alert.cluster_size,
            "avg_risk": alert.avg_risk,
            "is_acknowledged": alert.is_acknowledged,
            "is_dismissed": alert.is_dismissed,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]

    return Response(data)


@api_view(["POST"])
def acknowledge_alert(request, alert_id):
    """
    Mark alert as acknowledged
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.is_acknowledged = True
        alert.save()
        return Response({"message": "Alert acknowledged"})
    except Alert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=404)


@api_view(["POST"])
def dismiss_alert(request, alert_id):
    """
    Mark alert as dismissed
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.is_dismissed = True
        alert.save()
        return Response({"message": "Alert dismissed"})
    except Alert.DoesNotExist:
        return Response({"error": "Alert not found"}, status=404)