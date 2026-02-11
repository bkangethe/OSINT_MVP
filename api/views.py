from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import ListCreateAPIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import SignupForm, LoginForm
from Scrapers import x, facebook, instagram, nlp_, osint
from api.models import Profile, Platform, Target, RawJSONData, Post
from api import serializers


@login_required
def index(request):
    profiles_data = Profile.objects.all()
    profiles = serializers.ProfileSerializer(profiles_data, many=True).data

    context = {
        "profiles": profiles,
    }

    return render(request,"index.html", context=context)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
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
        

@api_view(["POST"])
def x_view(request):
    username = request.data.get("username")
    if not username:
        return Response(
            {"error": "Missing 'username' in request data"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        results = x.search_x(username)
        RawJSONData.objects.create(data=results)

        platform = Platform.objects.get(name="X")
        target, _ = Target.objects.get_or_create(name=username)

        if not results.get("people"):
            return Response(
                {"data": results, "message": "No users found for this username"},
                status=status.HTTP_200_OK
            )


        for person in results.get("people", []):
            profile, _  = Profile.objects.get_or_create(
                platform=platform,
                target=target,
                username=person.get("username"),
                defaults={"target": target}
            )

            profile.populate_from_data(person)
            profile.save()

        return Response({"data": results}, status=status.HTTP_200_OK)
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
    permission_classes = [AllowAny]


class XPostListCreateView(ListCreateAPIView):
    """
    List all saved X/Twitter posts or persist a single raw tweet.
    """
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data

        raw_tweet = data.get("raw_tweet")
        profile_username = data.get("profile_username")

        if not raw_tweet or not profile_username:
            return Response(
                {"error": "raw_tweet and profile_username are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if raw_tweet.get("text"):
            raw_tweet["text_analysis"] = nlp_.analyze_text(raw_tweet["text"])

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
        post.save()

        serializer = self.get_serializer(post)
        return Response(
            {
                "success": True,
                "created": created,
                "post": serializer.data,
            },
            status=status.HTTP_201_CREATED,
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