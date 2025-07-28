from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class MessageDeleteAPIViewTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            password="securepass123",
            first_name="John",
            last_name="Wick"
        )
        cls.user2 = User.objects.create_user(
            email="james@example.com",
            password="pass123",
            first_name="James",
            last_name="Smith"
        )
        cls.topic1 = cls.user.topics.create(topic_name="DevOps")
        cls.topic2 = cls.user.topics.create(topic_name="Docker")
        cls.room1 = cls.user.room_owner.create(
            topic=cls.topic1, room_name="Devops room", room_description="Devops room description")
        cls.room2 = cls.user.room_owner.create(
            topic=cls.topic1, room_name="Devops room 2", room_description="Devops room description 2")
        cls.room3 = cls.user2.room_owner.create(
            topic=cls.topic2, room_name="Docker room 2", room_description="Docker room description 2")

    def setUp(self):
        self.message_view_url = reverse(
            "room-details-message-create", kwargs={"pk": self.room1.id})
        self.client = APIClient()

    def create_message(self, owner=None, data=None):
        self.authenticate()
        post_data = data or {}
        response = self.client.post(
            self.message_view_url, {"body": "Testing"})

        return response

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_view_message_delete_success(self):
        create_response = self.create_message()
        message_id = create_response.data["messages"]["id"]
        message_delete_url = reverse(
            "message-delete", kwargs={"pk": message_id})
        response = self.client.delete(message_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["message"],
                         "Message deleted successfully")

    def test_view_message_delete_unauthorised_failed(self):
        create_response = self.create_message()
        message_id = create_response.data["messages"]["id"]
        message_delete_url = reverse(
            "message-delete", kwargs={"pk": message_id})
        self.authenticate(user=self.user2)
        response = self.client.delete(message_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"],
                         "Unauthorised to delete message.")

    def test_view_message_delete_unauthenticated_failed(self):
        message_delete_url = reverse(
            "message-delete", kwargs={"pk": self.room3.id})
        response = self.client.delete(message_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_message_delete_with_wrong_id_failed(self):
        self.authenticate()
        message_delete_url = reverse(
            "message-delete", kwargs={"pk": 100})
        response = self.client.delete(message_delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_view_message_delete_with_non_integer_pk(self):
        self.authenticate()
        message_delete_url = "api/messageDelete/abc/"
        response = self.client.delete(message_delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
