from django.urls import path, include
from rest_framework import routers

from train_service.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("crew", CrewViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_service"
