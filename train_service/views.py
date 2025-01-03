from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from train_service.models import Station
from train_service.serializers import StationSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
