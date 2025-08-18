from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import AirplaneType
from airport.tests.samples import (
    sample_admin,
    sample_user,
    sample_airplane_type,
)


class AirplaneTypeViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_admin()
        self.user = sample_user()
        self.airplane_type = sample_airplane_type(name="Boeing 737")
        self.list_url = reverse("airport:airplane_type-list")
        self.detail_url = reverse(
            "airport:airplane_type-detail", kwargs={"pk": self.airplane_type.pk}
        )

    def test_list_airplane_types_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_airplane_type_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Boeing 737")

    def test_create_airplane_type_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Airbus A320"}
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AirplaneType.objects.count(), 2)

    def test_create_airplane_type_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Airbus A320"}
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AirplaneType.objects.count(), 1)

    def test_update_airplane_type_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {"name": "Boeing 747"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airplane_type.refresh_from_db()
        self.assertEqual(self.airplane_type.name, "Boeing 747")

    def test_update_airplane_type_non_admin(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Boeing 747"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.airplane_type.refresh_from_db()
        self.assertEqual(self.airplane_type.name, "Boeing 737")

    def test_delete_airplane_type_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AirplaneType.objects.count(), 0)

    def test_delete_airplane_type_non_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(AirplaneType.objects.count(), 1)

    def test_access_airplane_type_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
