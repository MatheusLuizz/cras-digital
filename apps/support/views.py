from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SupportTicket, SupportMessage
from .serializers import SupportTicketSerializer, SupportMessageSerializer


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        tickets = SupportTicket.objects.filter(user=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SupportMessage.objects.all()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
