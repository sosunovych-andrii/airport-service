from django.db.models import QuerySet
from rest_framework import viewsets

from airport.models import AirplaneType, Airplane
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers.airplane import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer
)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]

    def get_queryset(self) -> QuerySet:
        queryset = Airplane.objects.all()
        if self.action in ("retrieve", "list"):
            queryset = queryset.select_related("airplane_type")

        airplane_name = self.request.query_params.get("name")
        if airplane_name:
            queryset = queryset.filter(name__icontains=airplane_name)

        return queryset

    def get_serializer_class(self) -> type[AirplaneSerializer]:
        serializer = AirplaneSerializer
        if self.action == "list":
            serializer = AirplaneListSerializer
        elif self.action == "retrieve":
            serializer = AirplaneRetrieveSerializer
        return serializer
