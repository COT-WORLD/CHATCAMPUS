from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class RoomViewTestCase(APITestCase):
    ROOM_DATA = {"topic": "Devops", "room_name": "DevOps Master Class",
                 "room_description": "A detailed introduction to DevOps core concepts, the difference between pre-DevOps and post-DevOps environments, Agile, Scrum, Kanban, CI/CD, infrastructure as code, monitoring, and more."}
    UPDATED_ROOM_DATA = {"topic": "Artificial Intelligence", "room_name": "Artificial Intelligence Discussion",
                         "room_description": "Discussion on artificial intelligence and its applications."}

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
            password="jamespass123",
            first_name="james",
            last_name="smith"
        )

    def setUp(self):
        self.client = APIClient()
        self.room_api_view_url = reverse("room-topic-create-list")

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def create_room(self, owner=None, data=None):
        self.authenticate(user=owner)
        post_data = data or {}
        response = self.client.post(self.room_api_view_url, {
            **self.ROOM_DATA, **post_data})
        return response

    def test_view_room_unauthenticated(self):
        response = self.client.get(self.room_api_view_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_room_authenticated(self):
        self.create_room()
        response = self.client.get(self.room_api_view_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("room", response.data)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"],
                         "Rooms retrieve successfully")

    def test_view_room_create_success(self):
        response = self.create_room()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Room created successfully")
        self.assertEqual(response.data["room"]["owner"]["id"], self.user.id)
        self.assertEqual(response.data["room"]
                         ["owner"]["email"], self.user.email)
        self.assertEqual(response.data["room"]
                         ["topic_details"]["topic_name"], "Devops")
        self.assertEqual(response.data["room"]
                         ["room_name"], "DevOps Master Class")
        self.assertIn("A detailed introduction to DevOps core concepts",
                      response.data["room"]["room_description"])

    def test_view_room_create_unauthenticated_failed(self):
        response = self.client.post(self.room_api_view_url, self.ROOM_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_room_create_failed_topic_missing(self):
        self.authenticate()
        data = {
            "room_name": self.ROOM_DATA["room_name"], "room_description": self.ROOM_DATA["room_description"]
        }
        response = self.client.post(self.room_api_view_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Room creation failed")
        self.assertIn("topic", response.data.get("errors", {}))

    def test_view_room_create_failed_room_name_missing(self):
        self.authenticate()
        data = {
            "topic": self.ROOM_DATA["topic"], "room_description": self.ROOM_DATA["room_description"]
        }
        response = self.client.post(self.room_api_view_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Room creation failed")
        self.assertIn("room_name", response.data.get("errors", {}))

    def test_view_room_create_failed_room_description_missing(self):
        self.authenticate()
        data = {
            "topic": self.ROOM_DATA["topic"], "room_name": self.ROOM_DATA["room_name"]
        }
        response = self.client.post(self.room_api_view_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Room creation failed")
        self.assertIn("room_description", response.data.get("errors", {}))

    def test_view_room_details_get_success(self):
        create_response = self.create_room()
        room_id = create_response.data["room"]["id"]
        room_detail_url = reverse(
            "room-get-update-delete", kwargs={"pk": room_id})
        response = self.client.get(room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         "Room retrieve successfully")
        self.assertEqual(response.data["room"]["owner"]["id"], self.user.id)
        self.assertEqual(response.data["room"]
                         ["owner"]["email"], self.user.email)
        self.assertEqual(response.data["room"]
                         ["topic_details"]["topic_name"], self.ROOM_DATA["topic"])
        self.assertEqual(response.data["room"]
                         ["room_name"], self.ROOM_DATA["room_name"])
        self.assertIn("A detailed introduction",
                      response.data["room"]["room_description"])

    def test_view_room_details_get_unauthenticated_failed(self):
        room_detail_url = reverse(
            "room-get-update-delete", kwargs={"pk": 1})
        response = self.client.get(room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_room_details_get_failed(self):
        self.create_room()
        room_detail_url = reverse(
            "room-get-update-delete", kwargs={"pk": 100})
        response = self.client.get(room_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_view_room_delete_success(self):
        create_response = self.create_room()
        room_id = create_response.data["room"]["id"]
        room_delete_url = reverse(
            "room-get-update-delete", kwargs={"pk": room_id})
        response = self.client.delete(room_delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["message"],
                         "Room deleted suceessfully")

    def test_view_room_delete_unauthorised_failed(self):
        create_response = self.create_room()
        room_id = create_response.data["room"]["id"]
        room_delete_url = reverse(
            "room-get-update-delete", kwargs={"pk": room_id})
        self.authenticate(user=self.user2)
        response = self.client.delete(room_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"],
                         "Unauthorised to delete this room.")

    def test_view_room_delete_unauthenticated_failed(self):
        room_delete_url = reverse(
            "room-get-update-delete", kwargs={"pk": 1})
        response = self.client.delete(room_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_room_details_delete_with_wrong_id_failed(self):
        self.create_room()
        room_delete_url = reverse(
            "room-get-update-delete", kwargs={"pk": 100})
        response = self.client.delete(room_delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_view_room_details_delete_without_id_failed(self):
        self.create_room()
        response = self.client.delete(self.room_api_view_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"],
                         "Room ID is required for delete.")

    def test_view_room_update_success(self):
        create_response = self.create_room()
        room_id = create_response.data["room"]["id"]
        room_update_url = reverse(
            "room-get-update-delete", kwargs={"pk": room_id})
        response = self.client.patch(room_update_url, self.UPDATED_ROOM_DATA)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Room updated successfully")
        self.assertEqual(response.data["room"]["owner"]["id"], self.user.id)
        self.assertEqual(response.data["room"]
                         ["owner"]["email"], self.user.email)
        self.assertEqual(response.data["room"]
                         ["topic_details"]["topic_name"], "Artificial Intelligence")
        self.assertEqual(response.data["room"]
                         ["room_name"], "Artificial Intelligence Discussion")
        self.assertIn("Discussion on artificial intelligence",
                      response.data["room"]["room_description"])

    def test_view_room_update_unauthenticated_failed(self):
        room_update_url = reverse(
            "room-get-update-delete", kwargs={"pk": 1})
        response = self.client.patch(room_update_url, self.UPDATED_ROOM_DATA)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_view_room_create_failed_topic_missing(self):
        create_response = self.create_room()
        room_id = create_response.data["room"]["id"]
        room_update_url = reverse(
            "room-get-update-delete", kwargs={"pk": room_id})
        data = {
            "room_name": self.UPDATED_ROOM_DATA["room_name"], "room_description": self.UPDATED_ROOM_DATA["room_description"]
        }
        response = self.client.patch(room_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Room update failed")
        self.assertIn("topic_name", response.data.get("errors", {}))

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

    def test_room_view_response_structure(self):
        self.authenticate()
        response = self.client.get(self.room_api_view_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"),
                         "Rooms retrieve successfully")

        rooms = response.data.get("room")
        self.assertIsInstance(rooms, list)

        for room in rooms:
            self.assertRoomFields(room)
