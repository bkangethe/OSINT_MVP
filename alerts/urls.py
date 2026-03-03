from django.urls import path
from .views import AlertListView, AcknowledgeAlertView, DismissAlertView

urlpatterns = [
    path("alerts/", AlertListView.as_view(), name="alert-list"),
    path("alerts/<int:pk>/acknowledge/", AcknowledgeAlertView.as_view(), name="acknowledge-alert"),
    path("alerts/<int:pk>/dismiss/", DismissAlertView.as_view(), name="dismiss-alert"),
]