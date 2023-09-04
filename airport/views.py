from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from django.db import models

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAdminOrIfAuthenticatedReadOnly
from .service import (
    AirportFilter,
    RouteFilter,
    CrewFilter,
    AirplaneFilter,
    FlightFilter,
    OrderFilter,
    get_client_ip,
)

from airport.models import (
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Rating,
)

from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    CreateRatingSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirportFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name (ex. ?name=name)",
            ),
            OpenApiParameter(
                "country",
                type=OpenApiTypes.STR,
                description="Filter by country (ex. ?country=country)",
            ),
            OpenApiParameter(
                "city",
                type=OpenApiTypes.STR,
                description="Filter by city (ex. ?city=city)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("destination", "source")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RouteFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type=OpenApiTypes.STR,
                description="Filter by source "
                            "(ex. ?source=source)",
            ),
            OpenApiParameter(
                "destination",
                type=OpenApiTypes.STR,
                description="Filter by destination "
                            "(ex. ?destination=destination)",
            ),
            OpenApiParameter(
                "distance",
                type=OpenApiTypes.INT,
                description="Filter by distance "
                            "(ex. ?distance=100)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AirplaneFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        airplane = (
            Airplane.objects.all()
            .annotate(
                rating_user=models.Count(
                    "ratings", filter=models.Q(
                        ratings__ip=get_client_ip(self.request))
                )
            )
            .annotate(
                middle_star=models.Sum(models.F("ratings__star"))
                / models.Count(models.F("ratings"))
            )
        )
        return airplane

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name (ex. ?name=name)",
            ),
            OpenApiParameter(
                "rows",
                type=OpenApiTypes.INT,
                description="Filter by rows "
                            "(ex. ?rows=10)",
            ),
            OpenApiParameter(
                "seats_in_row",
                type=OpenApiTypes.INT,
                description="Filter by seats_in_row "
                            "(ex. ?seats_in_row=5)",
            ),
            OpenApiParameter(
                "airplane_type",
                type=OpenApiTypes.STR,
                description="Filter by airplane_type "
                            "(ex. ?airplane_type=airplane_type)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CrewFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "crew_position",
                type=OpenApiTypes.STR,
                description="Filter by crew_position "
                            "(ex. ?crew_position=crew_position)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related(
        "route", "airplane").prefetch_related("crew").annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            ))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FlightFilter
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.STR,
                description="Filter by route (ex. ?route=route)",
            ),
            OpenApiParameter(
                "airplane",
                type=OpenApiTypes.STR,
                description="Filter by airplane "
                            "(ex. ?airplane=airplane)",
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description="Filter by departure_time "
                            "(ex. ?departure_time=DD-MM-YYYY)",
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.STR,
                description="Filter by arrival_time "
                            "(ex. ?arrival_time=DD-MM-YYYY)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__flight__airplane")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "created_at",
                type=OpenApiTypes.STR,
                description="Filter by created_at "
                            "(ex. ?created_at=YYYY-MM-DD HH:MM)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AddStarRatingView(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = CreateRatingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))
