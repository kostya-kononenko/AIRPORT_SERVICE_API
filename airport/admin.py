from django.contrib import admin

from airport.models import (
    Airport,
    Route,
    Crew,
    Airplane,
    AirplaneType,
    Flight,
    Order,
    Ticket
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "city", "closest_big_city")
    list_display_links = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    list_display_links = ("source",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "crew_position")
    list_display_links = ("first_name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "airplane_type")
    list_display_links = ("name",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("route", "airplane", "departure_time", "arrival_time")
    list_display_links = ("route",)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user")
    inlines = (TicketInline, )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("flight", "order", "row", "seat")
    list_display_links = ("flight",)


admin.site.register(AirplaneType)
