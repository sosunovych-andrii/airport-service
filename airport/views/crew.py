from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from airport.models import Crew
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers.crew import CrewSerializer


class CrewViewSet(viewsets.ModelViewSet):
    """
    Manage crew in the system.
    Supports listing, retrieving, creating, updating, and deleting.
    Read-only for authenticated users; full access for admins.
    """
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    serializer_class = CrewSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Crew.objects.all()

        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        position = self.request.query_params.get("position")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        if position:
            queryset = queryset.filter(position__exact=position)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="first_name",
                type=str,
                description="Filter by first_name (e.g., ?first_name=Andrii)",
                required=False
            ),
            OpenApiParameter(
                name="last_name",
                type=str,
                description="Filter by last_name (e.g., ?last_name=Shevchenko)",
                required=False
            ),
            OpenApiParameter(
                name="position",
                type=str,
                description="Filter by position",
                required=False,
                enum=["pilot", "attendant", "engineer"]
            )
        ]
    )
    def list(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return super().list(request, *args, **kwargs)
