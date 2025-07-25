from rest_framework import serializers
from .models import CrasLocation


class CrasLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrasLocation
        fields = '__all__'
