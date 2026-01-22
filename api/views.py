from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from Scrapers import x, facebook, instagram, nlp_, osint

def index(request):
    return render(request,"index.html")

@api_view(["POST"])
def get_data(request):
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
        # Call your existing function
        results = osint.basic_lookup(username)
        return Response({"data": results}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
