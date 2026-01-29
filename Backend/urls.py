from django.urls import path
from .views import index, osint_check, add_note

urlpatterns = [
    path("", index),
    path("api/check/", osint_check),
    path("api/note/", add_note),
]
