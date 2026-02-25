from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from collections import Counter
import numpy as np
from datetime import datetime
from django.db.models import Q

from .forms import SignupForm, LoginForm
from Scrapers import x, facebook, instagram, osint
from analysis import nlp, narrative, llm_summary
from analysis.graph import Graph
from api.models import Profile, Platform, Target, RawJSONData, Post
from api import serializers


@login_required
def index(request):
    profiles_data = Profile.objects.all()
    profiles = serializers.ProfileSerializer(profiles_data, many=True).data
    num_posts = Post.objects.count()
    alerts = Post.objects.filter(
        Q(text_analysis__risk="high") |  # hard
        Q(text_analysis__risk="medium", text_analysis__score__gt=0.8) |  # medium
        Q(text_analysis__risk="low", text_analysis__polarity__lt=-0.5)  # soft
    )

    flagged = Post.objects.filter(text_analysis__risk="high")

    # filterd posts
    filtered_posts = serializers.PostSerializer(Post.objects.filter(text_analysis__sentiment="negative"), many=True).data

 
    context = {
        "profiles": profiles,
        "num_posts": num_posts,
        "filtered_posts": filtered_posts,
        "alerts_count": alerts.count(),
        "flagged_count": flagged.count(),
    }

    return render(request,"index.html", context=context)


@api_view(["POST"])
def all_data(request):
    """
    API endpoint to run full basic_lookup on a target username.
    """
    username = request.data.get("username")
    print(username)
    
    if not username:
        return Response(
            {"error": "username field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        results = osint.basic_lookup(username)
        return Response({"data": results}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def create_or_update_post(raw_tweet, username):
    tweet_id = raw_tweet.get("id")
    if not tweet_id:
        return None

    url = f"https://x.com/{username}/status/{tweet_id}"

    post, _ = Post.objects.get_or_create(
        url=url,
        defaults={
            "date": raw_tweet.get("created_at"),
            "username": username,
        },
    )

    post.populate_from_data(raw_tweet, username=username)
    post.save()
    return post

@api_view(["POST"])
def x_search(request):
    username = request.data.get("username")
    username = username.lstrip("@")
    if not username:
        return Response(
            {"error": "Missing 'username' in request data"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        results = x.search_x(username)
        print(results)
        platform, _ = Platform.objects.get_or_create(name="X")

        if not results.get("people"):
            return Response(
                {"data": results, "message": "No users found for this username"},
                status=status.HTTP_200_OK
            )

        for person in results.get("people", []):
            profile, _  = Profile.objects.get_or_create(
                platform=platform,
                username=person.get("username")                
            )

            profile.populate_from_data(person)
            profile.save()

        for tweet in results.get("tweets",[]):
            post = create_or_update_post(tweet,username)
            
        return Response({
            "Profile saved": True,
            "Posts saved": len(results.get("tweets",[])),
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(["POST"])
def facebook_view(request):
    username = request.data.get("username")
    print(username)
    try:
        results = facebook.search_source_monitor(username)
        return Response({"data": results}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(["POST"])
def instagram_view(request):
    username = request.data.get("username")
    print(username)
    try:
        results = instagram.search_instagram(username)
        return Response({"data": results}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class XProfileListCreateView(ListCreateAPIView):
    """
    List all saved X/Twitter profiles or create a new one.
    """
    queryset = Profile.objects.filter(platform__name="X")
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsAuthenticated]


class XPostListCreateView(ListCreateAPIView):
    """
    List all saved X/Twitter posts or persist a single raw tweet.
    """

    serializer_class = serializers.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.filter(url__contains="x.com")

    def create(self, request, *args, **kwargs):
        raw_tweet = request.data.get("raw_tweet")
        profile_username = request.data.get("profile_username")

        if not raw_tweet or not profile_username:
            return Response(
                {"error": "raw_tweet and profile_username are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tweet_id = raw_tweet.get("id")
        if not tweet_id:
            return Response(
                {"error": "raw_tweet.id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://x.com/{profile_username}/status/{tweet_id}"

        post, created = Post.objects.get_or_create(
            url=url,
            defaults={
                "date": raw_tweet.get("created_at"),
                "username": profile_username,
            },
        )

        post.populate_from_data(raw_tweet, username=profile_username)
        text = raw_tweet.get("text")  
        if text:
            analysis_result = nlp.analyze_text(text)
            post.text_analysis = analysis_result  
        else:
            post.text_analysis = None

        post.save()

        return Response(
            {
                "success": True,
                "created": created,
                "post_id": post.id,
            },
            status=status.HTTP_201_CREATED,
        )
def build_network_description(graph_json):
    nodes = graph_json.get("nodes", [])
    metrics = graph_json.get("network_metrics", {})
    global_stats = graph_json.get("global_stats", {})

    density = metrics.get("density")
    avg_degree = metrics.get("average_degree")
    central_degree = metrics.get("central_nodes", {}).get("degree")

    node_lines = []
    for node in nodes:
        mentions = ", ".join(node.get("mentions", [])) or "no mentions"
        urls = len(node.get("urls", []))
        node_lines.append(
            f"{node['id']} has {node['tweet_count']} tweets, mentions {mentions}, and {urls} URLs."
        )

    top_mentions = global_stats.get("top_mentions", [])

    description = (
        f"Network density is {density:.2f}. Average degree is {avg_degree:.2f}. "
        f"The most central node by degree is {central_degree}. "
        + " ".join(node_lines)
        + f" Top mentions are: {', '.join(m for m, _ in top_mentions)}."
    )

    return description
    
@api_view(["GET"])
def graph_analysis(request):
    data = serializers.PostSerializer(Post.objects.all(), many=True).data
    graph = Graph(data)
    graph.create()
    graph_dict = graph.to_dict()
    
    description = build_network_description(graph_dict)
    
    return Response({"description": description,
                     "graph": graph_dict}, status=status.HTTP_200_OK)


@api_view(["POST"])
def nlp_analysis(request):
    text = request.data.get("text")
    if not text:
        return Response(
            {"error": "Missing 'text' in request data"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        results = nlp.analyze_text(text)
        return Response({"data": results}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST","GET"])
def narrative_clustering(request):
    data = serializers.PostSerializer(Post.objects.all()[:40], many=True).data
    texts = [item["text"] for item in data]
    timestamps = [item.get("date", datetime.utcnow()) for item in data]

    try:
        # engine and cluster
        engine = narrative.NarrativeClusterEngine()
        clusters = engine.cluster(texts)

        cluster_info = []
        for cluster in clusters:
            cluster_id = cluster["cluster_id"]
            posts = cluster["posts"]
            tweet_texts = [p["text"] for p in posts]

            # timestamps
            cluster_times = [p.get("timestamp", datetime.utcnow()) for p in posts]

            #  Burst detection
            burst_score = 0
            if cluster_times:
                hours = [t.hour for t in cluster_times]
                counts = Counter(hours)
                avg = np.mean(list(counts.values()))
                std = np.std(list(counts.values()))
                peak = max(counts.values())
                if peak > avg + std:
                    burst_score = 1  # emerging narrative

            # Coordination score: ratio of retweets
            retweet_count = sum(1 for t in tweet_texts if t.startswith("RT"))
            coordination_score = retweet_count / len(tweet_texts)

            cluster_info.append({
                "cluster_id": cluster_id,
                "num_tweets": len(tweet_texts),
                "tweets": tweet_texts,
                "coordinated_score": round(coordination_score, 2),
                "emerging_burst": bool(burst_score),
                "key_entities": None,  
                "sentiment": None,      
            })

        return Response({"clusters": cluster_info}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
def summary_view(request):
    text = request.data.get("text")
    print(text)
    if not text:
        return Response(
            {"error": "Missing 'text' in request data"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        summary = llm_summary.generate_summary(text)
        return Response({"summary": summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.email = form.cleaned_data["email"]
            user.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")