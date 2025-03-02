from django.urls import path, include
from rest_framework import routers

from train_service.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet,
    TripViewSet,
    OrderViewSet
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train_types", TrainTypeViewSet, basename="train-type")
router.register("trains", TrainViewSet)
router.register("crew", CrewViewSet)
router.register("trips", TripViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_service"
