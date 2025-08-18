from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets

from airport.models import Airport
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers.airport import AirportSerializer


class AirportViewSet(viewsets.ModelViewSet):
    """
    Manage airports in the system.
    Supports listing, retrieving, creating, updating, and deleting.
    Read-only for authenticated users; full access for admins.
    """
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    serializer_class = AirportSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Airport.objects.all()
        airport_name = self.request.query_params.get("name")
        if airport_name:
            queryset = queryset.filter(name__icontains=airport_name)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by name (e.g., ?name=Boryspil)",
                required=False
            )
        ]
    )
    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().list(request, *args, **kwargs)
