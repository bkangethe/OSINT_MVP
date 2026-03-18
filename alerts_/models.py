from django.db import models


class Alert(models.Model):

    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="low"
    )

    cluster_id = models.CharField(max_length=100, null=True, blank=True)
    cluster_size = models.IntegerField(default=0)
    avg_risk = models.FloatField(default=0.0)

    # Alert state controls
    is_acknowledged = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.severity})"