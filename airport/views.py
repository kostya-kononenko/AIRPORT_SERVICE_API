from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .service import (
    AirportFilter,
    RouteFilter,
    CrewFilter,
    AirplaneFilter,
    FlightFilter,
    OrderFilter,
)

from airport.models import (
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    RatingStarAirplane,
    Rating,
)

from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteListOrDetailSerializer,
    AirplaneSerializer,
    AirplaneListOrDetailSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirportFilter


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("destination", "source")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RouteFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListOrDetailSerializer
        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirplaneFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListOrDetailSerializer
        return AirplaneSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CrewFilter


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .prefetch_related("crew")
        .select_related("route", "airplane")
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FlightFilter

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
