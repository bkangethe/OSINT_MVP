from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view


from  alerts.models import Alert
from alerts.serializers import AlertSerializer

# Create your views here.


def sending_mail(subject, message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['thingamajig74@gmail.com'],
            fail_silently=False,
        )
        return Response({"message": "Email sent"},status=200)
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

@api_view(["GET"])
def alert_history(requests):
    data = AlertSerializer(Alert.objects.all(),many=True).data

    return Response({"data":data}, status=200)