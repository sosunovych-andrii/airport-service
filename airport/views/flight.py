from django.db.models import QuerySet, F, Count
from rest_framework import viewsets

from airport.models import Flight
from airport.parsers import (
    parse_int,
    parse_int_list,
    parse_date
)
from airport.serializers.flight import (
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer
)


class FlightViewSet(viewsets.ModelViewSet):
    def get_queryset(self) -> QuerySet:
        queryset = Flight.objects.all()
        if self.action in ("list", "retrieve"):
            queryset = (
                queryset
                .select_related(
                    "route__source",
                    "route__destination",
                    "airplane__airplane_type"
                )
                .prefetch_related(
                    "crew",
                    "tickets"
                )
            )
        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets", distinct=True)
                )
            )

        route_id = self.request.query_params.get("route_id")
        airplane_id = self.request.query_params.get("airplane_id")
        departure_time = self.request.query_params.get("departure_time")
        crew_ids = self.request.query_params.get("crew_ids")
        if route_id:
            queryset = queryset.filter(
                route_id=parse_int(route_id, "route_id")
            )
        if airplane_id:
            queryset = queryset.filter(
                airplane_id=parse_int(airplane_id, "airplane_id")
            )
        if crew_ids:
            queryset = queryset.filter(
                crew__id__in=parse_int_list(crew_ids, "crew_ids")
            )
        if departure_time:
            year, month, day = parse_date(
                departure_time, "departure_time"
            )
            queryset = queryset.filter(
                departure_time__year=year,
                departure_time__month=month,
                departure_time__day=day
            )

        return queryset.distinct()

    def get_serializer_class(self) -> type[FlightSerializer]:
        serializer = FlightSerializer
        if self.action == "list":
            serializer = FlightListSerializer
        elif self.action == "retrieve":
            serializer = FlightRetrieveSerializer
        return serializer
