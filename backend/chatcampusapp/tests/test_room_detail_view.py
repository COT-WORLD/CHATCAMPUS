from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.reverse import reverse

User = get_user_model()


class RoomDetailAPIViewTestCase(APITestCase):

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
        cls.room3 = cls.user.room_owner.create(
            topic=cls.topic2, room_name="Docker room 2", room_description="Docker room description 2")
        cls.message1 = cls.user.message_owner.create(
            room=cls.room1, body="DevOps is a modern approach for more reliable software delivery")
        cls.message2 = cls.user.message_owner.create(
            room=cls.room1, body="DevOps enables smoother, automated deployments.")
        cls.message4 = cls.user.message_owner.create(
            room=cls.room2, body="Docker is a tool that packages applications into lightweight containers.")
        cls.message5 = cls.user2.message_owner.create(
            room=cls.room2, body="Containers ensure consistency across development, testing, and production.")
        cls.message6 = cls.user2.message_owner.create(
            room=cls.room2, body="Docker enables smoother, automated deployments.")

    def setUp(self):
        self.client = APIClient()
        self.room_detail_url = reverse(
            "room-details-message-create", kwargs={"pk": self.room1.id})

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_room_detail_view_unauthenticated_failed(self):
        response = self.client.get(self.room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_room_detail_view_authenticated_success(self):
        self.authenticate()
        response = self.client.get(
            self.room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "Room details retrieve successfully")
        self.assertEqual(response.data.get("room")["id"], self.room1.id)
        self.assertEqual(response.data.get("room")[
                         "room_name"], self.room1.room_name)
        self.assertEqual(response.data.get("room")[
                         "room_description"], self.room1.room_description)
        self.assertEqual(response.data.get("room")[
                         "owner"]["id"], self.room1.owner.id)

    def test_room_detail_view_authenticated_wrong_room_id_failed(self):
        self.authenticate()
        response = self.client.get(reverse(
            "room-details-message-create", kwargs={"pk": 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

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

    def test_room_detail_view_response_structure(self):
        self.authenticate()
        response = self.client.get(
            self.room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "Room details retrieve successfully")
        self.assertEqual(response.data.get("message_count"),
                         self.room1.room_message.count())

        rooms = response.data.get("room")
        self.assertIsInstance(rooms, dict)
        self.assertRoomFields(rooms)

        participants = response.data.get("participants")
        self.assertIsInstance(participants, list)
        for participant in participants:
            self.assertUserFields(participant)

        room_messages = response.data.get("messages")
        self.assertIsInstance(room_messages, list)
        for room_message in room_messages:
            self.assertMessageFields(room_message)
