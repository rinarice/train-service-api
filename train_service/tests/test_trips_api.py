import datetime
from operator import itemgetter

from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_service.models import Trip
from train_service.serializers import TripListSerializer, TripDetailSerializer
from utils.samples import (
    sample_user,
    sample_trip,
    sample_route,
    sample_station,
    sample_train,
    sample_superuser
)

TRIP_URL = reverse("train_service:trip-list")
TRIP_DETAIL_URL = lambda pk: reverse(
    "train_service:trip-detail", kwargs={"pk": pk}
)

class UnauthenticatedTripApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRIP_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

        self.trip_1 = sample_trip()
        self.trip_2 = sample_trip(
            route=sample_route(
                source=sample_station(
                    name="new source station"
                ),
                destination=sample_station(
                    name="new destination station"
                )
            ),
            train=sample_train(),
            departure_time=datetime.datetime(year=2025, month=2, day=1),
            arrival_time=datetime.datetime(year=2025, month=2, day=2),
        )
        self.trips = Trip.objects.annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count("tickets")
            )
        )

    def test_list_trip(self):
        res = self.client.get(TRIP_URL)

        serializer = TripListSerializer(self.trips, many=True)
        serializer_data = sorted(serializer.data, key=itemgetter("id"))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer_data)

    def test_retrieve_trip(self):
        res = self.client.get(TRIP_DETAIL_URL(self.trip_1.id))

        serializer = TripDetailSerializer(self.trip_1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_forbidden(self):
        payload = {
            "route": sample_route().id,
            "train": sample_train().id,
            "departure_time": (
                    datetime.datetime.now() + datetime.timedelta(days=1)
            ),
            "arrival_time": (
                    datetime.datetime.now() + datetime.timedelta(days=2)
            ),
        }

        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_trips_by_departure_date(self):
        res = self.client.get(TRIP_URL, {"date": "2025-01-10"})

        serializer_1 = TripListSerializer(
            self.trips.get(id=self.trip_1.id)
        )
        serializer_2 = TripListSerializer(
            self.trips.get(id=self.trip_2.id)
        )

        self.assertNotIn(serializer_2.data, res.data["results"])
        self.assertIn(serializer_1.data, res.data["results"])

    def test_filter_trips_by_source(self):
        res = self.client.get(TRIP_URL, {"source": "new source station"})

        serializer_1 = TripListSerializer(
            self.trips.get(id=self.trip_1.id)
        )
        serializer_2 = TripListSerializer(
            self.trips.get(id=self.trip_2.id)
        )

        self.assertIn(serializer_2.data, res.data["results"])
        self.assertNotIn(serializer_1.data, res.data["results"])


class AdminTripApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_superuser()
        self.trip = sample_trip()
        self.client.force_authenticate(user=self.user)

    def test_create_trip(self):
        payload = {
            "route": sample_route().id,
            "train": sample_train().id,
            "departure_time": (
                datetime.datetime.now() + datetime.timedelta(days=1)
            ),
            "arrival_time": (
                datetime.datetime.now() + datetime.timedelta(days=2)
            )
        }
        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_trip_with_arrival_less_than_departure_date(self):
        payload = {
            "route": sample_route().id,
            "train": sample_train().id,
            "departure_time": (
                    datetime.datetime.now() + datetime.timedelta(days=2)
            ),
            "arrival_time": (
                    datetime.datetime.now() + datetime.timedelta(days=1)
            )
        }
        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            res.data.get("non_field_errors")[0],
            "Departure time must be before arrival time."
        )
