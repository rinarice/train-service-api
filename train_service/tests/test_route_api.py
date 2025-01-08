from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_service.models import Route
from train_service.serializers import (
    RouteListSerializer,
    RouteDetailSerializer
)
from utils.samples import (
    sample_user,
    sample_route,
    sample_station, sample_superuser
)

ROUTE_URL = reverse("train_service:route-list")
ROUTE_DETAIL_URL = lambda pk: reverse(
    "train_service:route-detail",
    kwargs={"pk": pk}
)


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.route = sample_route()
        self.client.force_authenticate(user=self.user)

    def test_list_routes(self):
        sample_route()

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)

    def test_retrieve_route(self):
        res = self.client.get(ROUTE_DETAIL_URL(self.route.id))

        serializer = RouteDetailSerializer(self.route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": sample_station(),
            "destination": sample_station(name="Station 1"),
            "distance": 10,
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class RouteFilteringTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

        self.station_1 = sample_station(name="Station A")
        self.station_2 = sample_station(name="Station B")
        self.station_3 = sample_station(name="Station C")
        self.route_1 = Route.objects.create(
            source=self.station_1, destination=self.station_2, distance=100
        )
        self.route_2 = Route.objects.create(
            source=self.station_2, destination=self.station_3, distance=150
        )
        self.route_3 = Route.objects.create(
            source=self.station_1, destination=self.station_3, distance=200
        )

    def test_filter_by_source(self):
        res = self.client.get(ROUTE_URL, {"source": "Station A"})
        routes = Route.objects.filter(source__name__icontains="Station A")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_by_destination(self):
        res = self.client.get(ROUTE_URL, {"destination": "Station C"})
        routes = Route.objects.filter(
            destination__name__icontains="Station C")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_by_source_and_destination(self):
        res = self.client.get(
            ROUTE_URL,
            {
                "source": "Station A",
                "destination": "Station C"
            }
        )
        routes = Route.objects.filter(
            source__name__icontains="Station A",
            destination__name__icontains="Station C"
        )
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_superuser()
        self.route = sample_route()
        self.client.force_authenticate(self.user)
        self.station_1 = sample_station(name="Station A")
        self.station_2 = sample_station(name="Station B")

    def test_create_station(self):
        payload = {
            "source": self.station_1.id,
            "destination": self.station_2.id,
            "distance": 150,
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        route = Route.objects.get(pk=res.data["id"])
        self.assertEqual(route.source, self.station_1)
        self.assertEqual(route.destination, self.station_2)
        self.assertEqual(route.distance, 150)

    def test_create_route_with_same_source_and_destination(self):
        payload = {
            "source": self.station_1.id,
            "destination": self.station_1.id,
            "distance": 150,
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)
        self.assertEqual(
            res.data["non_field_errors"][0],
            "Source and destination stations cannot be the same"
        )
