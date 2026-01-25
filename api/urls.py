from django.urls import path
from . import views

urlpatterns = [
path('check', views.all_data, name="get_data"),
path('x', views.x_view, name="x_view"),
path('facebook', views.facebook_view, name="facebook_view"),
path('instagram', views.instagram_view, name="instagram_view"),
]
