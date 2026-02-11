from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
path('check', views.all_data, name="get_data"),
path('x-search', views.x_view, name="x_view"),
path('x-posts',views.XPostListCreateView.as_view(), name="x_posts"),
path('x-profiles',views.XProfileListCreateView.as_view(), name="x_profiles"),
path('facebook', views.facebook_view, name="facebook_view"),
path('instagram', views.instagram_view, name="instagram_view"),

]

