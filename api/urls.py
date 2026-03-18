from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
path('check', views.all_data, name="get_data"),
path('x-search', views.x_search, name="x_view"),
path('x-posts',views.XPostListCreateView.as_view(), name="x_posts"),
path('x-profiles',views.XProfileListCreateView.as_view(), name="x_profiles"),
path('facebook', views.facebook_view, name="facebook_view"),
path('instagram', views.instagram_view, name="instagram_view"),
path('graph', views.graph_analysis,name="graph_analysis"),
path('nlp',views.nlp_analysis,name="nlp_analysis"),
path('narrative',views.narrative_clustering,name="narrative_analysis"),
path('summary',views.summary_view,name="summary_view"),
path("narratives/surges/", views.narrative_surges, name="narrative_surges"),
path("geolocation/mentions/", views.geolocation_analysis, name="geolocation_analysis"),
path("narratives/timeline/", views.narrative_timeline, name="narrative_timeline"),
path("intel/brief/", views.intel_brief, name="intel_brief"),
path("risk/scoring/", views.risk_scoring, name="risk_scoring"),
path("telegram/scrape/", views.TelegramScrapeAPIView.as_view(), name="telegram_scraper"),
]

