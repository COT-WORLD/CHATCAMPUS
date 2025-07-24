from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class TopicListAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            password="sucurepass123",
            first_name="John",
            last_name="Wick",
        )
        cls.topic1 = cls.user.topics.create(topic_name="DevOps")
        cls.topic2 = cls.user.topics.create(topic_name="Docker")

    def setUp(self):
        self.client = APIClient()
        self.topic_list_url = reverse("topic-list")

    def authenticate(self, creator=None):
        self.client.force_authenticate(user=creator or self.user)

    def test_topic_list_view_unauthenticated_failed(self):
        response = self.client.get(self.topic_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_topic_list_view_authenticated_success(self):
        self.authenticate()
        response = self.client.get(self.topic_list_url)
        self.assertEqual(response.data["message"],
                         "Topics retrieve successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.topic1.id, response.data["topic"][0]["id"])
        self.assertEqual(self.topic1.topic_name,
                         response.data["topic"][0]["topic_name"])
        self.assertEqual(self.user.id, response.data["topic"][0]["creator"])

    def test_topic_list_view_filter_by_q(self):
        self.authenticate()
        response = self.client.get(self.topic_list_url, {"q": "Dev"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         "Topics retrieve successfully")
        for topic in response.data["topic"]:
            self.assertIn("dev", topic["topic_name"].lower())

    def test_topic_list_view_filter_no_match(self):
        self.authenticate()
        response = self.client.get(self.topic_list_url, {
                                   "q": "nonexistenttopic"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         "Topics retrieve successfully")
        self.assertEqual(len(response.data["topic"]), 0)

    def test_topic_list_ordering_by_room_count(self):
        self.authenticate()
        self.user.room_owner.create(
            topic=self.topic1, room_name="Devops room", room_description="Devops room description")
        self.user.room_owner.create(
            topic=self.topic1, room_name="Devops room 2", room_description="Devops room description 2")
        self.user.room_owner.create(
            topic=self.topic2, room_name="Docker room 2", room_description="Docker room description 2")

        response = self.client.get(self.topic_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         "Topics retrieve successfully")
        # Topic1 should come before Topic2 because it has more rooms
        self.assertEqual(response.data["topic"][0]["id"], self.topic1.id)
        self.assertEqual(response.data["topic"][1]["id"], self.topic2.id)

    def test_topic_list_response_structure(self):
        self.authenticate()
        response = self.client.get(self.topic_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         "Topics retrieve successfully")
        for topic in response.data["topic"]:
            self.assertIn("id", topic)
            self.assertIn("topic_name", topic)
            self.assertIn("creator", topic)
            self.assertIn("room_count", topic)
