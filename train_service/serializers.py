from rest_framework import serializers

from train_service.models import Station, Route, TrainType


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs):
        if attrs.get("source") == attrs.get("destination"):
            raise serializers.ValidationError(
                "Source and destination stations cannot be the same"
            )
        return attrs


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")
