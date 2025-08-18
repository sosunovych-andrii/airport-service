from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    """
    Manage airplane_types in the system.
    Supports listing, retrieving, creating, updating, and deleting.
    Read-only for authenticated users; full access for admins.
    """
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    """
    Manage airplanes in the system.
    Supports listing, retrieving, creating, updating, and deleting.
    Read-only for authenticated users; full access for admins.
    """
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by name (e.g., ?name=Mriya)",
                required=False
            )
        ]
    )
    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().list(request, *args, **kwargs)
