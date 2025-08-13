from django.db.models import QuerySet
from rest_framework import viewsets

from airport.models import Crew
from airport.serializers.crew import CrewSerializer


class CrewViewSet(viewsets.ModelViewSet):
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
