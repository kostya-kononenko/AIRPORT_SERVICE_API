from datetime import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
)

from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer
)

FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        request = self.client.get(FLIGHT_URL)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin123456",
        )

        self.client.force_authenticate(self.user)

        self.countries = ["Ukraine", "USA"]

        self.cities = ["Kiev", "New york"]

        self.airports = [
            Airport.objects.create(
                name=f"Airport{self.cities[i]}",
                country=self.countries[i],
                city=self.cities[i],
                closest_big_city=f"New closest big city{self.cities[i]}"
            )
            for i in range(2)
        ]

        self.route = Route.objects.create(
            source=self.airports[0],
            destination=self.airports[1],
            distance=10000
        )

        self.airplane_type = AirplaneType.objects.create(
            name="New Airplane Type",
        )
        self.airplane = Airplane.objects.create(
            name="New airplane",
            rows=50,
            seats_in_row=11,
            airplane_type=self.airplane_type
        )

        self.crew = [
            Crew.objects.create(
                first_name=f"Name {letter}",
                last_name="Last name"
            )
            for letter in "abcde"
        ]

        self.departure_time = "2023-09-05 18:00"
        self.arrival_time = "2023-09-06 20:00"

        flights = [
            Flight.objects.create(
                route=self.route,
                airplane=self.airplane,
                departure_time=self.departure_time,
                arrival_time=self.arrival_time,
            )
            for i in range(2)
        ]

        for member in self.crew:
            flights[0].crew.add(member)
            flights[1].crew.add(member)

        for flight in flights:
            flight.save()

    def test_flight_list(self):
        request = self.client.get(FLIGHT_URL)

        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(request.status_code, status.HTTP_200_OK)

        for i in range(2):
            self.assertEqual(
                serializer.data[i]["route"],
                request.data[i]["route"]
            ),
            self.assertEqual(
                serializer.data[i]["airplane"],
                request.data[i]["airplane"]
            ),
            self.assertEqual(
                serializer.data[i]["departure_time"],
                request.data[i]["departure_time"]
            ),
            self.assertEqual(
                serializer.data[i]["arrival_time"],
                request.data[i]["arrival_time"]
            ),

    def test_retrieve_flight_detail(self):
        flights = Flight.objects.all()

        url = detail_url(flights[0].id)

        request = self.client.get(url)

        serializer = FlightDetailSerializer(flights[0])

        self.assertEqual(request.status_code, status.HTTP_200_OK)

        self.assertEqual(
            serializer.data["route"],
            request.data["route"]
        ),
        self.assertEqual(
            serializer.data["airplane"],
            request.data["airplane"]
        ),
        self.assertEqual(
            serializer.data["departure_time"],
            request.data["departure_time"]
        ),
        self.assertEqual(
            serializer.data["arrival_time"],
            request.data["arrival_time"]
        ),

        for i in range(len(self.crew)):
            self.assertEqual(
                serializer.data["crew"][i],
                request.data["crew"][i]
            ),

    def test_create_flight_forbidden(self):
        payload = {
            "route": self.route,
            "airplane": self.airplane,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
        }

        request = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="admin12345",
            is_staff=True,
        )

        self.client.force_authenticate(self.admin)

        self.countries = ["Ukraine", "USA"]

        self.cities = ["Kiev", "New york"]

        self.airports = [
            Airport.objects.create(
                name=f"Airport{self.cities[i]}",
                country=self.countries[i],
                city=self.cities[i],
                closest_big_city=f"New closest big city{self.cities[i]}"
            )
            for i in range(2)
        ]

        self.route = Route.objects.create(
            source=self.airports[0],
            destination=self.airports[1],
            distance=5000
        )

        self.airplane_type = AirplaneType.objects.create(
            name="New AirplaneType",
        )
        self.airplane = Airplane.objects.create(
            name="New Airplane",
            rows=50,
            seats_in_row=11,
            airplane_type=self.airplane_type
        )

        self.crew = [
            Crew.objects.create(
                first_name=f"First name {letter}",
                last_name="Last name"
            )
            for letter in "abcde"
        ]

        self.departure_time = "2023-09-05 18:00"
        self.arrival_time = "2023-09-06 20:00"

    def test_create_flight_success(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "crew": [
                crew.id
                for crew in self.crew
            ]
        }

        request = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=request.data["id"])

        crew = flight.crew.all()

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

        self.assertEqual(crew.count(), 5)
        for crew_member in self.crew:
            self.assertIn(crew_member, crew)

    def test_delete_flight_success(self):
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time
        )

        url = detail_url(flight.id)

        request = self.client.delete(url)

        self.assertEqual(
            request.status_code,
            status.HTTP_204_NO_CONTENT
        )
