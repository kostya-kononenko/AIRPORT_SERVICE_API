from django_filters import rest_framework as filters

from airport.models import Airport, Route, Crew, Airplane, Flight, Order


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class AirportFilter(filters.FilterSet):
    name = CharFilterInFilter(field_name="name", lookup_expr="in")
    country = CharFilterInFilter(field_name="country", lookup_expr="in")
    city = CharFilterInFilter(field_name="city", lookup_expr="in")

    class Meta:
        model = Airport
        fields = ["name", "country", "city"]


class RouteFilter(filters.FilterSet):
    source = CharFilterInFilter(field_name="source",
                                lookup_expr="in")
    destination = CharFilterInFilter(field_name="destination",
                                     lookup_expr="in")
    distance = filters.RangeFilter()

    class Meta:
        model = Route
        fields = ["source", "destination", "distance"]


class CrewFilter(filters.FilterSet):
    crew_position = CharFilterInFilter(field_name="crew_position",
                                       lookup_expr="in")

    class Meta:
        model = Crew
        fields = [
            "crew_position",
        ]


class AirplaneFilter(filters.FilterSet):
    name = CharFilterInFilter(field_name="name",
                              lookup_expr="in")
    rows = filters.RangeFilter()
    seats_in_row = filters.RangeFilter()
    airplane_type = CharFilterInFilter(field_name="airplane_type",
                                       lookup_expr="in")

    class Meta:
        model = Airplane
        fields = [
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
        ]


class FlightFilter(filters.FilterSet):
    route = CharFilterInFilter(field_name="route",
                               lookup_expr="in")
    airplane = CharFilterInFilter(field_name="airplane",
                                  lookup_expr="in")
    departure_time = filters.DateTimeFromToRangeFilter()
    arrival_time = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Flight
        fields = [
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
        ]


class OrderFilter(filters.FilterSet):
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Order
        fields = [
            "created_at",
        ]


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
