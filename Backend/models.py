from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    platform = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    url = models.URLField()
    threat_level = models.CharField(max_length=20, default="low")

class AnalystNote(models.Model):
    analyst = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    note = models.TextField()
    tags = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)