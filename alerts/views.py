from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from .serializers import AlertSerializer


class AlertListView(ListAPIView):
    queryset = Alert.objects.all().order_by("-created_at")
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]


class AcknowledgeAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
            alert.status = "ACKNOWLEDGED"
            alert.acknowledged_by = request.user
            alert.save()
            return Response({"message": "Alert acknowledged"})
        except Alert.DoesNotExist:
            return Response(
                {"error": "Alert not found"},
                status=status.HTTP_404_NOT_FOUND
            )
class DismissAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
            alert.status = "DISMISSED"
            alert.save()
            return Response({"message": "Alert dismissed"})
        except Alert.DoesNotExist:
            return Response(
                {"error": "Alert not found"},
                status=status.HTTP_404_NOT_FOUND
            )