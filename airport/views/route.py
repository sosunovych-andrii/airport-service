from django.db.models import QuerySet
from rest_framework import viewsets

from airport.models import Route
from airport.serializers.route import (
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer
)


class RouteViewSet(viewsets.ModelViewSet):
    def get_queryset(self) -> QuerySet:
        queryset = Route.objects.all()
        if self.action in ("retrieve", "list"):
            queryset = queryset.select_related("source", "destination")

        source_name = self.request.query_params.get("source_name")
        destination_name = self.request.query_params.get("destination_name")
        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)
        if destination_name:
            queryset = queryset.filter(destination__name__icontains=destination_name)

        return queryset

    def get_serializer_class(self) -> type[RouteSerializer]:
        serializer = RouteSerializer
        if self.action == "list":
            serializer = RouteListSerializer
        elif self.action == "retrieve":
            serializer = RouteRetrieveSerializer
        return serializer
