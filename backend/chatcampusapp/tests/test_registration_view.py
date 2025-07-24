from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAPITestCase(APITestCase):
    USER_DATA = {"email": "alice@example.com",
                 "password": "strongpass123",
                 "first_name": "Alice",
                 "last_name": "Wonderland",
                 "bio": "I'm a new user.", }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            password="sucurepass123",
            first_name="John",
            last_name="Doe",
        )

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User created successfully")
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]
                         ["email"], self.USER_DATA["email"])
        self.assertNotIn("password", response.data["user"])

    def test_register_user_with_html_in_first_name(self):
        self.USER_DATA["first_name"] = "<script>alert(1)</script>"
        response = self.client.post(self.register_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data["errors"])

    def test_register_user_with_invalid_avatar_url(self):
        self.USER_DATA["avatar"] = "http://127.0.0.1/malicious.png"
        response = self.client.post(self.register_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data["errors"])

    def test_register_user_response_structure(self):
        response = self.client.post(self.register_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "User created successfully")
        self.assertIn("id", response.data["user"])
        self.assertIn("first_name", response.data["user"])
        self.assertIn("last_name", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertIn("avatar", response.data["user"])
        self.assertIn("bio", response.data["user"])
        self.assertIn("last_login", response.data["user"])
