from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt

from Scrapers import x, facebook, instagram, nlp_, osint
from api.models import Profile, Platform, Target, RawJSONData

def index(request):
    return render(request,"index.html")

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