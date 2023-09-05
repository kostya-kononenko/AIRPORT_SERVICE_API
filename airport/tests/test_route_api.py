from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from airport.models import Route, Airport
from airport.serializers import (RouteListSerializer,
                                 RouteDetailSerializer)

ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id: int):
    return reverse("airport:route-detail", args=[route_id])


def sample_route(**params):
    source = Airport.objects.create(
        name="New airport1",
        country="Country1",
        city="City1",
        closest_big_city="City2",
    )

    destination = Airport.objects.create(
        name="New airport2",
        country="Country2",
        city="City3",
        closest_big_city="City4",
    )

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 5000,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_route(self):
        sample_route()
        res = self.client.get(ROUTE_URL, )
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()
        url = detail_url(route.id)
        res = self.client.get(url)
        serializer = RouteDetailSerializer(route)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = Airport.objects.create(
            name="New airport1",
            country="Country1",
            city="City1",
            closest_big_city="City2",
        )
        destination = Airport.objects.create(
            name="New airport2",
            country="Country2",
            city="City3",
            closest_big_city="City4",
        )
        payload = {
            "source": source,
            "destination": destination,
            "distance": 5000,
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_forbidden(self):
        route = sample_route()
        payload = {
            "distance": 6000,
        }
        url = detail_url(route.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_forbidden(self):
        route = sample_route()
        url = detail_url(route.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin12345", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route_success(self):
        source = Airport.objects.create(
            name="New airport10",
            country="Country10",
            city="City10",
            closest_big_city="City20",
        )
        destination = Airport.objects.create(
            name="New airport20",
            country="Country20",
            city="City30",
            closest_big_city="City40",
        )
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 5000,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_route_success(self):
        route = sample_route()
        payload = {
            "distance": 1000,
        }
        url = detail_url(route.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_route_success(self):
        route = sample_route()
        url = detail_url(route.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
