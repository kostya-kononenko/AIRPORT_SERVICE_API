from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from airport.models import Crew
from airport.serializers import CrewSerializer

CREW_URL = reverse("airport:crew-list")


def detail_url(crew_id: int):
    return reverse("airport:crew-detail", args=[crew_id])


def sample_crew(**params):

    defaults = {
        "first_name": "John",
        "last_name": "Smith",
        "crew_position": "Captain"
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


class UnauthenticatedCrewTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()
        res = self.client.get(CREW_URL, )
        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_crew_detail(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        res = self.client.get(url)
        serializer = CrewSerializer(crew)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "John",
            "last_name": "Smith",
            "crew_position": "Captain"
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_crew_forbidden(self):
        crew = sample_crew()
        payload = {
            "first_name": "Oleg",
            "last_name": "Ivanov",
            "crew_position": "First mate"
        }
        url = detail_url(crew.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_crew_forbidden(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew_success(self):
        payload = {
            "first_name": "Ivan",
            "last_name": "Petrov",
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_airplane_type_success(self):
        crew = sample_crew()
        payload = {
            "first_name": "Ivan",
        }
        url = detail_url(crew.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_crew_success(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
