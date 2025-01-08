from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from train_service.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Trip,
    Order,
)
from train_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from train_service.serializers import (
    StationSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    CrewSerializer,
    TripSerializer,
    TripListSerializer,
    TripDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    TrainDetailSerializer,
)
from user.models import User


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        source = self.request.query_params.get("source", None)
        destination = self.request.query_params.get("destination", None)

        queryset = self.queryset

        if source:
            queryset = queryset.filter(source__name__icontains=source)

        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    @extend_schema(
        description=(
            "Retrieve a list of routes with possibility of filtering "
            "by source and destination"
        ),
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter routes by source station name "
                "(e.g., ?source=Hogsmeade Station).",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter routes by destination station name "
                "(e.g., ?destination=Diagon Alley Station).",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Train.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TrainDetailSerializer
        return TrainSerializer


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            current_time = datetime.now()
            queryset = (
                queryset.select_related(
                    "route__source",
                    "route__destination",
                    "train"
                )
                .filter(departure_time__gt=current_time)
                .annotate(
                    tickets_available=(
                        F("train__cargo_num") * F("train__places_in_cargo")
                        - Count("tickets")
                    )
                )
            )
            departure_date = self.request.query_params.get("date", None)
            source = self.request.query_params.get("source", None)
            destination = self.request.query_params.get("destination", None)

            if departure_date:
                try:
                    date_obj = datetime.strptime(
                        departure_date, "%Y-%m-%d"
                    ).date()
                    queryset = queryset.filter(departure_time__date=date_obj)
                except ValueError:
                    raise ValidationError(
                        "Invalid date format. Use YYYY-MM-DD."
                    )

            if source:
                queryset = queryset.filter(
                    route__source__name__icontains=source
                )

            if destination:
                queryset = queryset.filter(
                    route__destination__name__icontains=destination
                )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripDetailSerializer
        return TripSerializer

    @extend_schema(
        description=(
            "Retrieve a list of trips with optional filters for source, "
            "destination, and departure date."
        ),
        parameters=[
            OpenApiParameter(
                "date",
                type=OpenApiTypes.DATE,
                description="Filter trips by date (YYYY-MM-DD) "
                "(e.g., ?date=2025-01-05).",
            ),
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter routes by source station name "
                "(e.g., ?source=Hogsmeade Station).",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter routes by destination station name "
                "(e.g., ?destination=Diagon Alley Station).",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 10


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Order.objects.prefetch_related(
        "tickets__trip__route__source",
        "tickets__trip__route__destination",
        "tickets__trip__train",
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=User.objects.first())
