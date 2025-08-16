from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class CreateUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("user:create")

    def test_create_user_with_valid_data(self):
        data = {"email": "user@example.com", "password": "qwerty123"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="user@example.com").exists())

    def test_create_user_with_invalid_data(self):
        data = {"email": "user@example.com", "password": "12345"}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="user@example.com").exists())


class ManageUserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="qwerty123"
        )
        self.client = APIClient()
        self.url = reverse("user:manage")

    def test_manage_user_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manage_user_retrieve_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manage_user_update_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {"email": "new_email@example.com"}
        response = self.client.patch(self.url, data=data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data["email"])
