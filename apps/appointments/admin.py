from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'time', 'status']
    list_filter = ['status', 'date']
    search_fields = ['user__username', 'description']
