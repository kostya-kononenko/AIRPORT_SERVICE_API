from django.urls import path
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneViewSet,
    AirplaneTypeViewSet,
    FlightViewSet,
    CrewViewSet,
    OrderViewSet,
    AddStarRatingView,
)

router = routers.DefaultRouter()
router.register("airport", AirportViewSet)
router.register("route", RouteViewSet)
router.register("airplane-type", AirplaneTypeViewSet)
router.register("airplane", AirplaneViewSet)
router.register("crew", CrewViewSet)
router.register("flight", FlightViewSet)
router.register("order", OrderViewSet)
router.register("rating", AddStarRatingView)


urlpatterns = router.urls

app_name = "airport"
