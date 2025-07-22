from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileViewTestCase(APITestCase):
    def setUp(self):
        self.profile_url = reverse("user-profile")

        self.user = User.objects.create_user(
            email="john@example.com",
            password="securepass123",
            first_name="John",
            last_name="Doe",
        )

        self.client = APIClient()

    def test_view_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_update_profile_bio(self):
        self.client.force_authenticate(user=self.user)
        new_bio = "Updated_bio"
        response = self.client.patch(
            self.profile_url, {"bio": new_bio})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["bio"], new_bio)

    def test_update_profile_invalid_bio_html(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.profile_url, {"bio": "<h1>Evil</h1>"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("bio", response.data["errors"])

    def test_update_profile_password_hashing(self):
        self.client.force_authenticate(user=self.user)
        new_password = "newsecure123"
        response = self.client.patch(
            self.profile_url, {"password": new_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # load updated user
        self.assertEqual(self.user.check_password(
            new_password), True)  # password is hashed
