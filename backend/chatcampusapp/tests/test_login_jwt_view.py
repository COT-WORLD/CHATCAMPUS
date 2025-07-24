from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UserLoginJWTViewTestCase(APITestCase):
    USER_DATA = {
        "email": "john@example.com",
        "password": "securepass123",
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            password="securepass123",
            first_name="John",
            last_name="Wick",
        )

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("token_obtain_pair")

    def get_token_for_user(self, user=None):
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def test_user_login_success(self):
        response = self.client.post(self.login_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_wrong_email(self):
        self.USER_DATA["email"] = "james@example.com"
        response = self.client.post(self.login_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "No active account found with the given credentials")

    def test_user_login_wrong_password(self):
        self.USER_DATA["password"] = "wrongpassword"
        response = self.client.post(self.login_url, self.USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"], "No active account found with the given credentials")

    def test_user_profile_with_jwt_token(self):
        tokens = self.get_token_for_user()

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(reverse("user-profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_user_refresh_token(self):
        tokens = self.get_token_for_user()

        response = self.client.post(reverse("token_refresh"), {
            "refresh": tokens["refresh"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
