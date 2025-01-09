from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_service.models import Station
from train_service.serializers import StationSerializer
from utils.samples import (
    sample_user,
    sample_station,
    sample_superuser
)

STATION_URL = reverse("train_service:station-list")
STATION_DETAIL_URL = lambda pk: reverse(
    "train_service:station-detail", kwargs={"pk": pk}
)


class UnauthenticatedStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.station = sample_station()
        self.client.force_authenticate(self.user)

    def test_list_stations(self):
        sample_station()

        res = self.client.get(STATION_URL)

        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)

    def test_retrieve_station(self):
        res = self.client.get(STATION_DETAIL_URL(self.station.id))

        serializer = StationSerializer(self.station)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_station_forbidden(self):
        payload = {
            "name": "New Station",
            "latitude": 12.34,
            "longitude": 10.12,
        }
        res = self.client.post(STATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_superuser()
        self.station = sample_station()
        self.client.force_authenticate(self.user)

    def test_create_station(self):
        payload = {
            "name": "New Station",
            "latitude": 12.34,
            "longitude": 10.12,
        }

        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        station = Station.objects.get(pk=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(station, key))
