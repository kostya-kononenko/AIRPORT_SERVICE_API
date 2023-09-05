from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from airport.models import Airport
from airport.serializers import AirportSerializer

AIRPORT_URL = reverse("airport:airport-list")


def detail_url(airport_id: int):
    return reverse("airport:airport-detail", args=[airport_id])


def sample_airport(**params):

    defaults = {
        "name": "New airport",
        "country": "Country",
        "city": "City",
        "closest_big_city": "New city",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        sample_airport()
        res = self.client.get(AIRPORT_URL, )
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airport_detail(self):
        airport = sample_airport()
        url = detail_url(airport.id)
        res = self.client.get(url)
        serializer = AirportSerializer(airport)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "Very new airport",
            "country": "Country",
            "city": "City",
            "closest_big_city": "Very new city",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airport_forbidden(self):
        airport = sample_airport()
        payload = {
            "name": "New name",
        }
        url = detail_url(airport.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_forbidden(self):
        airport = sample_airport()
        url = detail_url(airport.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airport_success(self):
        payload = {
            "name": "AIRPORT",
            "country": "COUNTRY",
            "city": "NEW CITY",
            "closest_big_city": "CITY",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_airport_success(self):
        airport = sample_airport()
        payload = {
            "name": "New name",
            "country": "New country",
        }
        url = detail_url(airport.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_airport_success(self):
        airport = sample_airport()
        url = detail_url(airport.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
