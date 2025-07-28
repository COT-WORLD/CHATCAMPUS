from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class MessageCreateAPIViewTestCase(APITestCase):

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

    def test_view_message_create_unauthenticated_failed(self):
        response = self.client.post(self.message_view_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_message_create_with_non_integer_pk(self):
        self.authenticate()
        message_delete_url = "api/roomDetails/abc/"
        response = self.client.post(message_delete_url, {"body": "testing"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_message_create_authenticated_wrong_room_id_failed(self):
        self.authenticate()
        response = self.client.post(reverse(
            "room-details-message-create", kwargs={"pk": 100}), {"body": "Testing"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_view_message_create_authenticate_success(self):
        self.authenticate()
        response = self.client.post(
            self.message_view_url, {"body": "Testing"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"),
                         "Message created successfully")
        self.assertEqual(response.data.get("messages")["body"], "Testing")
        self.assertEqual(response.data.get("messages")[
                         "room"]["id"], self.room1.id)
        self.assertEqual(response.data.get("messages")[
                         "owner"]["id"], self.room1.owner.id)

    def test_view_message_create_with_blank_body_authenticate_failed(self):
        self.authenticate()
        response = self.client.post(
            self.message_view_url, {"body": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"),
                         "Message body is required")

    def test_view_message_create_with_whitespace_in_body_authenticate_failed(self):
        self.authenticate()
        response = self.client.post(
            self.message_view_url, {"body": "   "})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"),
                         "Message body is required")

    def test_view_message_create_with_allowed_tags(self):
        self.authenticate()
        html_body = '<p>Paragraph <strong>Bold</strong> <a href="https://a.com" rel="noopener">link</a></p>'
        response = self.client.post(self.message_view_url, {"body": html_body})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('<p>Paragraph <strong>Bold</strong> <a href="https://a.com" rel="noopener">link</a></p>',
                      response.data['messages']['body'])

    def test_view_message_create_with_script_tag_authenticate_success(self):
        self.authenticate()
        response = self.client.post(
            self.message_view_url, {"body": "<script>alert('testing')</script>"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"),
                         "Message created successfully")
        self.assertEqual(response.data.get("messages")[
                         "body"], "&lt;script&gt;alert('testing')&lt;/script&gt;")
        self.assertEqual(response.data.get("messages")[
                         "room"]["id"], self.room1.id)
        self.assertEqual(response.data.get("messages")[
                         "owner"]["id"], self.room1.owner.id)

    def assertUserFields(self, user):
        for field in ["id", "first_name", "last_name", "email", "avatar", "bio", "last_login"]:
            self.assertIn(field, user)

    def assertTopicFields(self, topic):
        for field in ["id", "topic_name", "creator"]:
            self.assertIn(field, topic)

    def assertRoomFields(self, room):
        for field in [
            "id", "owner", "topic_details", "room_name", "room_description",
            "participants", "created_at"
        ]:
            self.assertIn(field, room)

        self.assertIsInstance(room["owner"], dict)
        self.assertUserFields(room["owner"])

        self.assertIsInstance(room["topic_details"], dict)
        self.assertTopicFields(room["topic_details"])

        self.assertIsInstance(room["participants"], list)
        for participant in room["participants"]:
            self.assertUserFields(participant)

    def assertMessageFields(self, room_message):
        for field in [
            "id", "owner", "room", "body", "created_at"
        ]:
            self.assertIn(field, room_message)

        self.assertIsInstance(room_message["owner"], dict)
        self.assertUserFields(room_message["owner"])

        self.assertIsInstance(room_message["room"], dict)
        self.assertRoomFields(room_message["room"])

    def test_view_message_create_response_structure(self):
        response = self.create_message()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"),
                         "Message created successfully")

        messages = response.data.get("messages")
        self.assertIsInstance(messages, dict)
        self.assertMessageFields(messages)
