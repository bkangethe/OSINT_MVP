from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from Backend.models import Profile, AnalystNote
from Backend.analysis.threat import assess_threat
from Backend.analysis.clustering import cluster_topics
from Backend.analysis.graph import build_graph
from Backend.osint.basic_lookup import basic_lookup

def index(request):
    return render(request, "index.html")

@csrf_exempt
def osint_check(request):
    data = json.loads(request.body)
    username = data.get("username")

    results = basic_lookup(username)

    for p in results["profiles"]:
        threat = assess_threat(p.get("bio", ""))
        topics = cluster_topics(p.get("posts", []))
        p["threat"] = threat
        p["topics"] = topics

    graph = build_graph(results["profiles"])
    results["graph"] = graph

    return JsonResponse(results)

@login_required
@csrf_exempt
def add_note(request):
    data = json.loads(request.body)
    profile = Profile.objects.get(id=data["profile_id"])

    AnalystNote.objects.create(
        analyst=request.user,
        profile=profile,
        note=data["note"],
        tags=data["tags"]
    )

    return JsonResponse({"status": "saved"})
