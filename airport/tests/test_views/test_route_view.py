from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from airport.models import Route
from airport.tests.samples import (
    sample_admin,
    sample_user,
    sample_airport,
    sample_route,
)


class RouteViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.user = sample_user()
        self.airport1 = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        self.airport2 = sample_airport(name="Lviv Airport", closest_big_city="Lviv")
        self.route = sample_route(
            source=self.airport1, destination=self.airport2, distance=500
        )
        self.list_url = reverse("airport:route-list")
        self.detail_url = reverse("airport:route-detail", kwargs={"pk": self.route.pk})

    def test_list_routes_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["distance"], 500)

    def test_list_routes_filter_by_source_name(self):
        sample_route(source=self.airport2, destination=self.airport1, distance=500)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"source_name": "Boryspil"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_routes_filter_by_destination_name(self):
        sample_route(source=self.airport2, destination=self.airport1, distance=500)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"destination_name": "Lviv Airport"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_route_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["distance"], 500)

    def test_create_route_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "source": self.airport2.pk,
            "destination": self.airport1.pk,
            "distance": 600,
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 2)
        self.assertEqual(response.data["source"], self.airport2.pk)
        self.assertEqual(response.data["destination"], self.airport1.pk)
        self.assertEqual(response.data["distance"], 600)

    def test_create_route_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "source": self.airport2.pk,
            "destination": self.airport1.pk,
            "distance": 600,
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Route.objects.count(), 1)

    def test_update_route_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "source": self.airport2.pk,
            "destination": self.airport1.pk,
            "distance": 700,
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.route.refresh_from_db()
        self.assertEqual(self.route.source_id, self.airport2.pk)
        self.assertEqual(self.route.destination_id, self.airport1.pk)
        self.assertEqual(self.route.distance, 700)

    def test_update_route_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "source": self.airport2.pk,
            "destination": self.airport1.pk,
            "distance": 700,
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.route.refresh_from_db()
        self.assertEqual(self.route.source_id, self.airport1.pk)
        self.assertEqual(self.route.destination_id, self.airport2.pk)
        self.assertEqual(self.route.distance, 500)

    def test_delete_route_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Route.objects.count(), 0)

    def test_delete_route_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Route.objects.count(), 1)

    def test_access_route_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
