from rest_framework import serializers

from train_service.models import Station


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "city")
