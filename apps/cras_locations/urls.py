from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrasLocationViewSet

router = DefaultRouter()
router.register('cras-locations', CrasLocationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
