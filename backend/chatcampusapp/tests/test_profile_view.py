from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileViewTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            password="securepass123",
            first_name="John",
            last_name="Doe",
        )

    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse("user-profile")

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_view_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_profile_authenticated_and_response_structure(self):
        self.authenticate()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         "User profile retrieve successfully")
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertIn("id", response.data["user"])
        self.assertIn("first_name", response.data["user"])
        self.assertIn("last_name", response.data["user"])
        self.assertIn("email", response.data["user"])
        self.assertIn("avatar", response.data["user"])
        self.assertIn("bio", response.data["user"])
        self.assertIn("last_login", response.data["user"])

    def test_update_profile_bio(self):
        self.authenticate()
        new_bio = "Updated_bio"
        response = self.client.patch(
            self.profile_url, {"bio": new_bio})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["bio"], new_bio)

    def test_update_profile_invalid_bio_html(self):
        self.authenticate()
        response = self.client.patch(
            self.profile_url, {"bio": "<h1>Evil</h1>"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("bio", response.data["errors"])

    def test_update_profile_password_hashing(self):
        self.authenticate()
        new_password = "newsecure123"
        response = self.client.patch(
            self.profile_url, {"password": new_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # load updated user
        self.assertEqual(self.user.check_password(
            new_password), True)  # password is hashed
