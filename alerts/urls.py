from django.urls import path
from . import views

urlpatterns = [
    path("history/", views.alert_history),
    path("acknowledge/<int:alert_id>/", views.acknowledge_alert),
    path("dismiss/<int:alert_id>/", views.dismiss_alert),
]