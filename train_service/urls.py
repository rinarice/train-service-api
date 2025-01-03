from django.urls import path, include
from rest_framework import routers

from train_service.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("train_types", TrainTypeViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "train_service"
