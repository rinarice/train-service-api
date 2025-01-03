from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from train_service.models import Station, Route, TrainType
from train_service.serializers import (
    StationSerializer,
    RouteSerializer,
    TrainTypeSerializer
)


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
