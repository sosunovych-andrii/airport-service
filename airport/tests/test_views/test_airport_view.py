from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from airport.models import Airport
from airport.tests.samples import sample_admin, sample_user, sample_airport


class AirportViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.user = sample_user()
        self.airport = sample_airport(name="Boryspil", closest_big_city="Kyiv")
        self.list_url = reverse("airport:airport-list")
        self.detail_url = reverse(
            "airport:airport-detail", kwargs={"pk": self.airport.pk}
        )

    def test_list_airports_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Boryspil")
        self.assertEqual(response.data["results"][0]["closest_big_city"], "Kyiv")

    def test_list_airports_filter_by_name(self):
        sample_airport(name="Lviv Airport", closest_big_city="Lviv")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"name": "Boryspil"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Boryspil")

    def test_retrieve_airport_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Boryspil")

    def test_create_airport_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Lviv Airport", "closest_big_city": "Lviv"}
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 2)

    def test_create_airport_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Lviv Airport", "closest_big_city": "Lviv"}
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Airport.objects.count(), 1)

    def test_update_airport_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Updated Boryspil", "closest_big_city": "Kyiv City"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airport.refresh_from_db()
        self.assertEqual(self.airport.name, "Updated Boryspil")
        self.assertEqual(self.airport.closest_big_city, "Kyiv City")

    def test_update_airport_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Boryspil", "closest_big_city": "Kyiv City"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.airport.refresh_from_db()
        self.assertEqual(self.airport.name, "Boryspil")
        self.assertEqual(self.airport.closest_big_city, "Kyiv")

    def test_delete_airport_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Airport.objects.count(), 0)

    def test_delete_airport_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Airport.objects.count(), 1)

    def test_access_airport_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
