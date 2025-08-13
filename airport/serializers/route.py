from rest_framework import serializers

from airport.models import Route
from airport.serializers.airport import AirportSerializer


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "distance",
            "source",
            "destination",
            "full_route"
        )

    def validate(self, attrs: dict) -> dict | None:
        attrs = super().validate(attrs)
        Route.validate_source_not_equals_destination(
            source=attrs["source"],
            destination=attrs["destination"],
            error_to_raise=serializers.ValidationError
        )
        return attrs


class RouteListSerializer(RouteSerializer):
    class Meta(RouteSerializer.Meta):
        fields = ("id", "distance", "full_route")


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)
