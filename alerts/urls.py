from django.urls import path

from alerts import views

urlpatterns = [
    path("history",views.alert_history, name="alert_history")

]