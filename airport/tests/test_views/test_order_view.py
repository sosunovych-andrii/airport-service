from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from airport.models import Order, Ticket
from airport.tests.samples import (
    sample_user,
    sample_airport,
    sample_route,
    sample_airplane_type,
    sample_airplane,
    sample_flight,
    sample_order,
    sample_ticket,
)


class OrderViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(email="user1@example.com")
        self.other_user = sample_user(email="other@example.com")
        self.airport1 = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        self.airport2 = sample_airport(name="Lviv Airport", closest_big_city="Lviv")
        self.route = sample_route(
            source=self.airport1, destination=self.airport2, distance=500
        )
        self.airplane_type = sample_airplane_type(name="Boeing 737")
        self.airplane = sample_airplane(
            name="Mriya", rows=10, seats_in_row=10, airplane_type=self.airplane_type
        )
        self.flight = sample_flight(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        self.order = sample_order(user=self.user)
        self.ticket = sample_ticket(
            order=self.order, flight=self.flight, row=1, seat_in_row=1
        )
        self.other_order = sample_order(user=self.other_user)
        self.other_ticket = sample_ticket(
            order=self.other_order, flight=self.flight, row=2, seat_in_row=2
        )
        self.list_url = reverse("airport:order-list")
        self.detail_url = reverse("airport:order-detail", kwargs={"pk": self.order.pk})
        self.other_detail_url = reverse(
            "airport:order-detail", kwargs={"pk": self.other_order.pk}
        )

    def test_list_orders_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.order.pk)
        self.assertEqual(len(response.data["results"][0]["tickets"]), 1)
        self.assertEqual(response.data["results"][0]["tickets"][0]["row"], 1)
        self.assertEqual(response.data["results"][0]["tickets"][0]["seat_in_row"], 1)

    def test_list_orders_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.other_order.pk)
        self.assertEqual(response.data["results"][0]["tickets"][0]["row"], 2)
        self.assertEqual(response.data["results"][0]["tickets"][0]["seat_in_row"], 2)

    def test_list_orders_filter_by_flight_id(self):
        order2 = sample_order(user=self.user)
        flight2 = sample_flight(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now() + timedelta(days=1),
            arrival_time=timezone.now() + timedelta(days=1, hours=2),
        )
        sample_ticket(order=order2, flight=flight2, row=3, seat_in_row=3)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"flight_id": self.flight.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.order.pk)
        self.assertEqual(
            response.data["results"][0]["tickets"][0]["flight"]["id"], self.flight.pk
        )

    def test_list_orders_filter_by_created_at(self):
        created_at = self.order.created_at.date().isoformat()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"created_at": created_at})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.order.pk)

    def test_retrieve_order_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.pk)
        self.assertEqual(len(response.data["tickets"]), 1)
        self.assertEqual(
            response.data["tickets"][0]["flight"]["route"]["source"]["name"], "Boryspil"
        )
        self.assertEqual(response.data["tickets"][0]["row"], 1)
        self.assertEqual(response.data["tickets"][0]["seat_in_row"], 1)

    def test_retrieve_order_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {"tickets": [{"flight": self.flight.pk, "row": 3, "seat_in_row": 3}]}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 3)
        self.assertEqual(Ticket.objects.count(), 3)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 2)
        self.assertEqual(response.data["tickets"][0]["flight"], self.flight.pk)
        self.assertEqual(response.data["tickets"][0]["row"], 3)
        self.assertEqual(response.data["tickets"][0]["seat_in_row"], 3)

    def test_create_order_invalid_ticket(self):
        self.client.force_authenticate(user=self.user)
        data = {"tickets": [{"flight": 999, "row": 3, "seat_in_row": 3}]}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Ticket.objects.count(), 2)

    def test_delete_order_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Ticket.objects.filter(order=self.order).count(), 0)
        self.assertEqual(Order.objects.filter(user=self.other_user).count(), 1)

    def test_delete_order_other_user(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Ticket.objects.filter(order=self.order).count(), 1)

    def test_access_order_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
