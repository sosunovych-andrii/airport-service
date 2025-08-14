from django.db.models import QuerySet, Prefetch
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from airport.models import Order, Ticket
from airport.parsers import parse_int, parse_date
from airport.serializers.order import (
    OrderSerializer,
    OrderRetrieveSerializer,
    OrderListSerializer,
    OrderCreateSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        queryset = Order.objects.filter(user=self.request.user)
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                Prefetch(
                    "tickets",
                    queryset=Ticket.objects.select_related(
                        "flight__route__source",
                        "flight__route__destination",
                        "flight__airplane"
                    )
                ),
                "tickets__flight__crew"
            )

        flight_id = self.request.query_params.get("flight_id")
        created_at = self.request.query_params.get("created_at")
        if flight_id:
            queryset = queryset.filter(
                tickets__flight_id=parse_int(flight_id, "flight_id")
            )
        if created_at:
            year, month, day = parse_date(created_at, "created_at")
            queryset = queryset.filter(
                created_at__year=year,
                created_at__month=month,
                created_at__day=day
            )

        return queryset.distinct()


    def get_serializer_class(self) -> type[OrderSerializer]:
        serializer = OrderSerializer
        if self.action == "retrieve":
            serializer = OrderRetrieveSerializer
        elif self.action == "list":
            serializer = OrderListSerializer
        elif self.action == "create":
            serializer = OrderCreateSerializer
        return serializer

    def perform_create(self, serializer: OrderSerializer) -> None:
        serializer.save(user=self.request.user)
