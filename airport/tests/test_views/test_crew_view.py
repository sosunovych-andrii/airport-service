from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from airport.models import Crew
from airport.tests.samples import sample_admin, sample_user, sample_crew


class CrewViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.user = sample_user()
        self.crew = sample_crew(
            first_name="Andrii", last_name="Shevchenko", position="pilot"
        )
        self.list_url = reverse("airport:crew-list")
        self.detail_url = reverse("airport:crew-detail", kwargs={"pk": self.crew.pk})

    def test_list_crew_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_crew_filter_by_first_name(self):
        sample_crew(first_name="Olena", last_name="Koval", position="attendant")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"first_name": "Andrii"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["first_name"], "Andrii")

    def test_list_crew_filter_by_last_name(self):
        sample_crew(first_name="Olena", last_name="Koval", position="attendant")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"last_name": "Shevchenko"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["last_name"], "Shevchenko")

    def test_list_crew_filter_by_position(self):
        sample_crew(first_name="Olena", last_name="Koval", position="attendant")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"position": "pilot"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["position"], "pilot")

    def test_retrieve_crew_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Andrii")
        self.assertEqual(response.data["last_name"], "Shevchenko")
        self.assertEqual(response.data["position"], "pilot")

    def test_create_crew_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"first_name": "Olena", "last_name": "Koval", "position": "attendant"}
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 2)
        self.assertEqual(response.data["first_name"], "Olena")
        self.assertEqual(response.data["last_name"], "Koval")
        self.assertEqual(response.data["position"], "attendant")

    def test_create_crew_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "Olena", "last_name": "Koval", "position": "attendant"}
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Crew.objects.count(), 1)

    def test_update_crew_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "first_name": "Updated Andrii",
            "last_name": "Updated Shevchenko",
            "position": "engineer",
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.crew.refresh_from_db()
        self.assertEqual(self.crew.first_name, "Updated Andrii")
        self.assertEqual(self.crew.last_name, "Updated Shevchenko")
        self.assertEqual(self.crew.position, "engineer")

    def test_update_crew_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "first_name": "Updated Andrii",
            "last_name": "Updated Shevchenko",
            "position": "engineer",
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.crew.refresh_from_db()
        self.assertEqual(self.crew.first_name, "Andrii")
        self.assertEqual(self.crew.last_name, "Shevchenko")
        self.assertEqual(self.crew.position, "pilot")

    def test_delete_crew_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Crew.objects.count(), 0)

    def test_delete_crew_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Crew.objects.count(), 1)

    def test_access_crew_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
