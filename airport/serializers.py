from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
    RatingStarAirplane,
    Rating,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "country",
            "city",
            "closest_big_city",
            "image",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )


class RouteListOrDetailSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
            "image",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "rating_user",
            "middle_star",
        )


class AirplaneListOrDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("first_name", "last_name", "crew_position", "image")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
        )


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False)
    airplane = serializers.StringRelatedField(many=False)
    crew_count = serializers.SerializerMethodField()

    def get_crew_count(self, obj):
        return obj.crew.count()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew_count",
            "departure_time",
            "arrival_time",
        )


class FlightDetailSerializer(FlightSerializer):
    route = RouteListOrDetailSerializer(many=False)
    airplane = AirplaneListOrDetailSerializer(many=False)
    crew = CrewSerializer(many=True)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "tickets",
        )

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("star", "airplane", "ip")

        def create(self, validate_data):
            rating = Rating.objects.update_or_create(
                ip=validate_data.get("ip", None),
                airplane=validate_data.get("airplane", None),
                defaults={"star": validate_data.get("star")},
            )
            return rating
