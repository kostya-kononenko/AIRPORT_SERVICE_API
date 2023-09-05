from unittest import mock

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from airport.models import Airplane, AirplaneType
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
)

AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id: int):
    return reverse("airport:airplane-detail", args=[airplane_id])


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="Airplane555")

    defaults = {
        "name": "Sample airplane",
        "rows": 20,
        "seats_in_row": 5,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
        )
        self.client.force_authenticate(self.user)

    @mock.patch("airport.service.get_client_ip")
    def test_list_airplane(self, mock_get_client_ip):
        mock_get_client_ip.return_value = "127.1.1.1."
        sample_airplane()
        res = self.client.get(
            AIRPLANE_URL,
        )
        airplanes = (
            Airplane.objects.all()
            .annotate(
                rating_user=models.Count(
                    "ratings", filter=models.Q(ratings__ip=mock_get_client_ip())
                )
            )
            .annotate(
                middle_star=models.Sum(models.F("ratings__star"))
                / models.Count(models.F("ratings"))
            )
        )
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)
        res = self.client.get(url)
        serializer = AirplaneDetailSerializer(airplane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Sample airplane",
            "rows": 20,
            "seats_in_row": 5,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_forbidden(self):
        airplane = sample_airplane()
        payload = {
            "name": "New name",
        }
        url = detail_url(airplane.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_forbidden(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane_success(self):
        airplane_type = AirplaneType.objects.create(name="Airplane555")
        payload = {
            "name": "Sample airplane",
            "rows": 20,
            "seats_in_row": 5,
            "airplane_type": airplane_type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_airplane_success(self):
        airplane = sample_airplane()
        payload = {
            "name": "New name",
        }
        url = detail_url(airplane.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_airplane_success(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
