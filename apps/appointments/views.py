from rest_framework import viewsets, permissions
from .models import Appointment
from .serializers import AppointmentSerializer
from .permissions import IsOwnerOrProfessional


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwnerOrProfessional()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'professional':
            return Appointment.objects.all()
        return Appointment.objects.filter(user=user)
