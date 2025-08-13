from rest_framework import serializers

from airport.models import Ticket
from airport.serializers.flight import (
    FlightListSerializer,
    FlightNestedSerializer
)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat_in_row",
            "flight"
        )

    def validate(self, attrs: dict) -> dict | None:
        attrs = super().validate(attrs)
        airplane = attrs["flight"].airplane
        Ticket.validate_row_and_seat_within_capacity(
            row=attrs["row"],
            airplane_rows=airplane.rows,
            seat_in_row=attrs["seat_in_row"],
            airplane_seats_in_row=airplane.seats_in_row,
            error_to_raise=serializers.ValidationError
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightNestedSerializer(many=False, read_only=True)
