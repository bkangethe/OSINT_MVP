from django.db import models
from django.contrib.auth.models import User


class Alert(models.Model):

    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('DISMISSED', 'Dismissed'),
    )

    title = models.CharField(max_length=255)
    narrative = models.TextField()
    cluster_id = models.CharField(max_length=100, blank=True, null=True)

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='LOW'
    )

    score = models.FloatField(default=0.0)
    mention_count = models.IntegerField(default=0)

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    acknowledged_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.title} - {self.severity}"