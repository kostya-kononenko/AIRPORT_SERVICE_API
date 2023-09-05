from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airport:airplanetype-list")


def detail_url(airplane_type_id: int):
    return reverse("airport:airplanetype-detail", args=[airplane_type_id])


def sample_airplane_type(**params):

    defaults = {
        "name": "Airplane Boing 747",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane_type(self):
        sample_airplane_type()
        res = self.client.get(AIRPLANE_TYPE_URL, )
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airplane_type_detail(self):
        airplane_type = sample_airplane_type()
        url = detail_url(airplane_type.id)
        res = self.client.get(url)
        serializer = AirplaneTypeSerializer(airplane_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "Sample airplane type",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_type_forbidden(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "New name",
        }
        url = detail_url(airplane_type.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_type_forbidden(self):
        airplane_type = sample_airplane_type()
        url = detail_url(airplane_type.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_type_success(self):
        payload = {
            "name": "Very new airplane",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_airplane_type_success(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "New name",
        }
        url = detail_url(airplane_type.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_airplane_type_success(self):
        airplane_type = sample_airplane_type()
        url = detail_url(airplane_type.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
