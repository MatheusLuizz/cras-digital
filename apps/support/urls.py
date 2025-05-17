from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupportTicketViewSet, SupportMessageViewSet

router = DefaultRouter()
router.register('tickets', SupportTicketViewSet, basename='support-ticket')
router.register('messages', SupportMessageViewSet, basename='support-message')

urlpatterns = [
    path('', include(router.urls)),
    path('my-tickets/', SupportTicketViewSet.as_view({'get': 'my_tickets'}), name='my-tickets'),
]
