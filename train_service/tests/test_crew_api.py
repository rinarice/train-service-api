from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from train_service.models import Crew
from train_service.serializers import CrewSerializer
from utils.samples import sample_user, sample_crew, sample_superuser

CREW_URL = reverse("train_service:crew-list")


class UnauthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.crew = sample_crew()
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_list_crew(self):
        sample_crew()

        res = self.client.get(CREW_URL)

        crews = Crew.objects.all()

        serializer = CrewSerializer(crews, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_superuser()
        self.client.force_authenticate(user=self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        crew = Crew.objects.get(pk=res.data["id"])
        for key in payload.keys():
            self.assertEqual(res.data[key], getattr(crew, key))
