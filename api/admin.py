from django.contrib import admin
from api import models

# Register your models here.
admin.site.register(models.RawJSONData)
admin.site.register(models.Target)
admin.site.register(models.Platform)
admin.site.register(models.Profile)
admin.site.register(models.Post)
admin.site.register(models.CrossPlatformProfile)
