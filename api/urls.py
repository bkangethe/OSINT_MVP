from django.urls import path
from . import views

urlpatterns = [
path('check', views.all_data, name="get_data"),
path('x', views.x_view, name="x_view"),
path('x_save', views.save_x_tweet, name="x_save_view"),  
path('x_list', views.XPostListView.as_view(), name="x_list_view"),
path('facebook', views.facebook_view, name="facebook_view"),
path('instagram', views.instagram_view, name="instagram_view"),
]
