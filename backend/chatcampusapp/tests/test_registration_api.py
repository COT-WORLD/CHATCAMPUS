from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')

        self.user = User.objects.create_user(
            email="john@example.com",
            password="sucurepass123",
            first_name="John",
            last_name="Doe",
        )
        self.client = APIClient()

    def test_register_user_success(self):
        data = {
            "email": "alice@example.com",
            "password": "strongpass123",
            "first_name": "Alice",
            "last_name": "Wonderland",
            "bio": "I'm a new user.",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "alice@example.com")
        self.assertNotIn("password", response.data["user"])

    def test_register_user_with_html_in_first_name(self):
        data = {
            "email": "evil@example.com",
            "password": "evilpass123",
            "first_name": "<script>alert(1)</script>",
            "last_name": "Test",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data["errors"])

    def test_register_user_with_invalid_avatar_url(self):
        data = {
            "email": "avatar@example.com",
            "password": "avatarpass123",
            "first_name": "Test",
            "last_name": "Test",
            "avatar": "http://127.0.0.1/malicious.png",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data["errors"])
