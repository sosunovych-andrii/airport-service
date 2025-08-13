from rest_framework import serializers

from airport.models import Flight, Ticket
from airport.serializers.crew import CrewNestedSerializer
from airport.serializers.route import RouteRetrieveSerializer
from airport.serializers.airplane import (
    AirplaneNestedSerializer,
    AirplaneRetrieveSerializer
)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "duration",
            "route",
            "airplane",
            "crew"
        )

    def validate(self, attrs: dict) -> dict | None:
        attrs = super().validate(attrs)
        Flight.validate_min_arrival_time(
            arrival_time=attrs["arrival_time"],
            departure_time=attrs["departure_time"],
            error_to_raise=serializers.ValidationError
        )
        return attrs


class FlightListSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="full_route"
    )
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    airplane = AirplaneNestedSerializer(
        many=False,
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta(FlightSerializer.Meta):
        fields = (
            "id",
            "departure_time",
            "duration",
            "route",
            "airplane",
            "crew",
            "tickets_available"
        )


class FlightRetrieveSerializer(FlightSerializer):
    class _TicketTakenPlacesSerializer(serializers.ModelSerializer):
        class Meta:
            model = Ticket
            fields = ("row", "seat_in_row")

    taken_places = _TicketTakenPlacesSerializer(
        many=True,
        read_only=True,
        source="tickets"
    )
    route = RouteRetrieveSerializer(many=False, read_only=True)
    airplane = AirplaneRetrieveSerializer(many=False, read_only=True)
    crew = CrewNestedSerializer(many=True, read_only=True)

    class Meta(FlightSerializer.Meta):
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "duration",
            "route",
            "airplane",
            "crew",
            "taken_places"
        )


class FlightNestedSerializer(FlightSerializer):
    route = RouteRetrieveSerializer(many=False, read_only=True)
    airplane = AirplaneNestedSerializer(many=False, read_only=True)
    crew = CrewNestedSerializer(many=True, read_only=True)
