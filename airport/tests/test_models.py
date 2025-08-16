from datetime import  timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from airport.models import Route, Flight, Ticket
from airport.tests.samples import (
    sample_airport,
    sample_flight,
    sample_route,
    sample_airplane,
    sample_order,
    sample_user
)


class RouteModelTest(TestCase):
    def test_source_equals_destination(self):
        airport = sample_airport()
        route = Route(
            distance=1000,
            source=airport,
            destination=airport
        )
        with self.assertRaises(ValidationError):
            route.save()

    def test_source_not_equals_destination(self):
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        route = Route(
            distance=1000,
            source=source,
            destination=destination
        )
        route.save()
        self.assertEqual(Route.objects.count(), 1)


class FlightModelTest(TestCase):
    def test_invalid_arrival_time(self):
        flight = Flight(
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            route=sample_route(),
            airplane=sample_airplane()
        )
        with self.assertRaises(ValidationError):
            flight.save()

    def test_valid_arrival_time(self):
        flight = Flight(
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
            route=sample_route(),
            airplane=sample_airplane()
        )
        flight.save()
        self.assertEqual(Flight.objects.count(), 1)


class TicketModelTest(TestCase):
    def test_row_and_seat_not_within_capacity(self):
        ticket = Ticket(
            row=11,
            seat_in_row=11,
            order=sample_order(sample_user()),
            flight=sample_flight()
        )
        with self.assertRaises(ValidationError):
            ticket.save()

    def test_row_and_seat_within_capacity(self):
        ticket = Ticket(
            row=10,
            seat_in_row=10,
            order=sample_order(sample_user()),
            flight=sample_flight()
        )
        ticket.save()
        self.assertEqual(Ticket.objects.count(), 1)
