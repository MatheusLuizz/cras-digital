from rest_framework import viewsets
from .models import CrasLocation
from .serializers import CrasLocationSerializer


class CrasLocationViewSet(viewsets.ModelViewSet):
    queryset = CrasLocation.objects.all()
    serializer_class = CrasLocationSerializer
