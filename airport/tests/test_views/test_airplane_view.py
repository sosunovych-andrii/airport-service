from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airplane
from airport.tests.samples import (
    sample_admin,
    sample_user,
    sample_airplane_type,
    sample_airplane,
)


class AirplaneViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.user = sample_user()
        self.airplane_type = sample_airplane_type(name="Boeing 737")
        self.airplane = sample_airplane(
            name="Mriya", rows=10, seats_in_row=10, airplane_type=self.airplane_type
        )
        self.list_url = reverse("airport:airplane-list")
        self.detail_url = reverse(
            "airport:airplane-detail", kwargs={"pk": self.airplane.pk}
        )

    def test_list_airplanes_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Mriya")

    def test_list_airplanes_filter_by_name(self):
        sample_airplane(
            name="Dreamliner", rows=8, seats_in_row=8, airplane_type=self.airplane_type
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"name": "Mriya"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Mriya")

    def test_retrieve_airplane_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Mriya")

    def test_create_airplane_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Antonov",
            "rows": 12,
            "seats_in_row": 12,
            "airplane_type": self.airplane_type.pk,
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airplane.objects.count(), 2)
        self.assertEqual(response.data["name"], "Antonov")

    def test_create_airplane_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Antonov",
            "rows": 12,
            "seats_in_row": 12,
            "airplane_type": self.airplane_type.pk,
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Airplane.objects.count(), 1)

    def test_update_airplane_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Updated Mriya",
            "rows": 15,
            "seats_in_row": 15,
            "airplane_type": self.airplane_type.pk,
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airplane.refresh_from_db()
        self.assertEqual(self.airplane.name, "Updated Mriya")
        self.assertEqual(self.airplane.rows, 15)
        self.assertEqual(self.airplane.seats_in_row, 15)

    def test_update_airplane_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Updated Mriya",
            "rows": 15,
            "seats_in_row": 15,
            "airplane_type": self.airplane_type.pk,
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.airplane.refresh_from_db()
        self.assertEqual(self.airplane.name, "Mriya")
        self.assertEqual(self.airplane.rows, 10)
        self.assertEqual(self.airplane.seats_in_row, 10)

    def test_delete_airplane_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Airplane.objects.count(), 0)

    def test_delete_airplane_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Airplane.objects.count(), 1)

    def test_access_airplane_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
