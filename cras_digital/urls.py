from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="CRAS Digital API",
        default_version='v1',
        description="API documentation for CRAS Digital",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mlfs7@discente.ifpe.edu.br"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.authentication.urls')),
    path('api/v1/', include('apps.appointments.urls')),
    path('api/v1/', include('apps.support.urls')),
    path('api/v1/', include('apps.services.urls')),
    path('api/v1/', include('apps.cras_locations.urls')),
]
