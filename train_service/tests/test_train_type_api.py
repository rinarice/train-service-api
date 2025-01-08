from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_service.models import TrainType
from train_service.serializers import TrainTypeSerializer
from utils.samples import sample_train_type, sample_user, sample_superuser

TRAIN_TYPE_URL = reverse("train_service:train-type-list")


class UnauthenticatedTrainTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.train_type = sample_train_type()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_train_type(self):
        sample_train_type()

        res = self.client.get(TRAIN_TYPE_URL)

        train_types = TrainType.objects.all()
        serializer = TrainTypeSerializer(train_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)

    def test_create_forbidden(self):
        payload = {
            "name": "Test Name"
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTrainTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_superuser()
        self.train_type = sample_train_type()
        self.client.force_authenticate(user=self.user)

    def test_create_train_type(self):
        payload = {
            "name": "Test Name",
        }

        res = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
