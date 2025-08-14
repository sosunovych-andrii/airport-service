from django.db.models import QuerySet
from rest_framework import viewsets

from airport.models import Airport
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers.airport import AirportSerializer


class AirportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
    serializer_class = AirportSerializer

    def get_queryset(self) -> QuerySet:
        queryset = Airport.objects.all()
        airport_name = self.request.query_params.get("name")
        if airport_name:
            queryset = queryset.filter(name__icontains=airport_name)
        return queryset
