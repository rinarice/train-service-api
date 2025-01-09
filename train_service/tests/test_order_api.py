from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_service.models import Order
from train_service.serializers import OrderSerializer
from utils.samples import sample_user, sample_order, sample_trip

ORDER_URL = reverse("train_service:order-list")


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_order(self):
        sample_order(user=self.user)
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL)

        orders = Order.objects.filter(user=self.user)
        serializer = OrderSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_order(self):
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "trip": sample_trip().id
                }
            ]
        }
        res = self.client.post(ORDER_URL, data=payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
