from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from airport.models import Flight
from airport.tests.samples import (
    sample_admin,
    sample_user,
    sample_airport,
    sample_route,
    sample_airplane_type,
    sample_airplane,
    sample_crew,
    sample_flight,
)


class FlightViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.user = sample_user()
        self.airport1 = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        self.airport2 = sample_airport(name="Lviv Airport", closest_big_city="Lviv")
        self.route = sample_route(
            source=self.airport1, destination=self.airport2, distance=500
        )
        self.airplane_type = sample_airplane_type(name="Boeing 737")
        self.airplane = sample_airplane(
            name="Mriya", rows=10, seats_in_row=10, airplane_type=self.airplane_type
        )
        self.crew1 = sample_crew(
            first_name="Andrii", last_name="Shevchenko", position="pilot"
        )
        self.crew2 = sample_crew(
            first_name="Olena", last_name="Koval", position="attendant"
        )
        self.flight = sample_flight(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        self.flight.crew.add(self.crew1, self.crew2)
        self.list_url = reverse("airport:flight-list")
        self.detail_url = reverse(
            "airport:flight-detail", kwargs={"pk": self.flight.pk}
        )

    def test_list_flights_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_flights_filter_by_route_id(self):
        route2 = sample_route(
            source=self.airport2, destination=self.airport1, distance=500
        )
        sample_flight(
            route=route2,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"route_id": self.route.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_flights_filter_by_airplane_id(self):
        airplane2 = sample_airplane(
            name="Dreamliner", rows=8, seats_in_row=8, airplane_type=self.airplane_type
        )
        sample_flight(
            route=self.route,
            airplane=airplane2,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"airplane_id": self.airplane.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["airplane"]["id"], self.airplane.pk
        )

    def test_list_flights_filter_by_departure_time(self):
        departure_time = timezone.now().date().isoformat()
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"departure_time": departure_time})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_flights_filter_by_crew_ids(self):
        crew3 = sample_crew(first_name="Ivan", last_name="Petrov", position="engineer")
        flight2 = sample_flight(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timedelta(hours=2),
        )
        flight2.crew.add(crew3)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.list_url, {"crew_ids": f"{self.crew1.pk},{self.crew2.pk}"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_flight_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["route"]["source"]["name"], "Boryspil")
        self.assertEqual(response.data["airplane"]["name"], "Mriya")
        self.assertEqual(len(response.data["crew"]), 2)

    def test_create_flight_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "route": self.route.pk,
            "airplane": self.airplane.pk,
            "departure_time": timezone.now() + timedelta(days=1),
            "arrival_time": timezone.now() + timedelta(days=1, hours=2),
            "crew": [self.crew1.pk, self.crew2.pk],
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 2)
        self.assertEqual(len(response.data["crew"]), 2)

    def test_update_flight_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "route": self.route.pk,
            "airplane": self.airplane.pk,
            "departure_time": (timezone.now() + timedelta(days=2)).isoformat(),
            "arrival_time": (timezone.now() + timedelta(days=2, hours=2)).isoformat(),
            "crew": [self.crew1.pk],
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.crew.count(), 2)
        self.assertEqual(self.flight.route.pk, self.route.pk)
        self.assertEqual(self.flight.airplane.pk, self.airplane.pk)

    def test_update_flight_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "route": self.route.pk,
            "airplane": self.airplane.pk,
            "departure_time": (timezone.now() + timedelta(days=2)).isoformat(),
            "arrival_time": (timezone.now() + timedelta(days=2, hours=2)).isoformat(),
            "crew": [self.crew1.pk],
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.crew.count(), 1)
        self.assertEqual(self.flight.crew.first().pk, self.crew1.pk)
        self.assertEqual(self.flight.route.pk, self.route.pk)
        self.assertEqual(self.flight.airplane.pk, self.airplane.pk)

    def test_update_flight_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"crew": [self.crew1.pk]}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.crew.count(), 2)

    def test_delete_flight_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flight.objects.count(), 0)

    def test_delete_flight_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Flight.objects.count(), 1)

    def test_access_flight_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
