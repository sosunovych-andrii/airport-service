from django.db import transaction
from rest_framework import serializers

from airport.models import Order, Ticket
from airport.serializers.ticket import (
    TicketListSerializer,
    TicketSerializer,
    TicketRetrieveSerializer
)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)


class OrderCreateSerializer(OrderSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    @transaction.atomic()
    def create(self, validated_data: dict) -> Order:
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(order=order, **ticket_data)
        return order
