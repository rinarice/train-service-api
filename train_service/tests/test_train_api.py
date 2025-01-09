from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from train_service.models import Train
from train_service.serializers import TrainSerializer, TrainDetailSerializer
from utils.samples import (
    sample_user,
    sample_train,
    sample_train_type,
    sample_superuser
)

TRAIN_URL = reverse("train_service:train-list")
TRAIN_DETAIL_URL = lambda pk: reverse(
    "train_service:train-detail", kwargs={"pk": pk}
)


class UnauthorizedTrainApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.train = sample_train()
        self.client.force_authenticate(user=self.user)

    def test_list_trains(self):
        sample_train()

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.all()
        serializers = TrainSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializers.data)

    def test_retrieve_train(self):
        res = self.client.get(TRAIN_DETAIL_URL(self.train.id))

        serializer = TrainDetailSerializer(self.train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        train_type = sample_train_type()
        payload = {
            "name": "New Train",
            "cargo_num": 5,
            "places_in_cargo": 10,
            "train_type": train_type.id,
        }

        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_superuser()
        self.train = sample_train()
        self.client.force_authenticate(user=self.user)

    def test_create_train(self):
        payload = {
            "name": "New Train",
            "cargo_num": 5,
            "places_in_cargo": 10,
            "train_type": sample_train_type().id,
        }
        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_train(self):
        payload = {"name": "New Train"}
        res = self.client.patch(TRAIN_DETAIL_URL(self.train.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
