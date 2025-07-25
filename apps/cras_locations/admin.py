from django.contrib import admin
from .models import CrasLocation


@admin.register(CrasLocation)
class CrasLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'zip_code', 'phone')
    search_fields = ('name', 'zip_code')
