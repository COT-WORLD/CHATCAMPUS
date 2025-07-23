from urllib.parse import urlparse
from rest_framework import serializers
from .models import Room, Topic, User
from PIL import Image


# Custom User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email",
                  "password", "avatar", "bio", "last_login"]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "avatar": {"required": False, "allow_null": True},
        }

    # validate first name
    def validate_first_name(self, value):
        if '<' in value or '>' in value:
            raise serializers.ValidationError(
                "First name cannot contain HTML.")
        return value

    # validate last name
    def validate_last_name(self, value):
        if '<' in value or '>' in value:
            raise serializers.ValidationError("Last Name cannot contain HTML.")
        return value

    # validate bio
    def validate_bio(self, value):
        if '<' in value or '>' in value:
            raise serializers.ValidationError("Bio cannot contain HTML.")
        return value

    def validate_avatar(self, value):
        # check for SSRF via URLs
        if isinstance(value, str):
            parsed = urlparse(value)
            if parsed.hostname in ["127.0.0.1", "localhost"]:
                raise serializers.ValidationError("Invalid avatar URL.")

        # check uploaded file is a real image
        if hasattr(value, "file"):
            try:
                image = Image.open(value)
                image.varify()
            except Exception:
                raise serializers.ValidationError(
                    "Uploaded file is not a valid image.")
        return value

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


# Topic Serializer
class TopicSerializer(serializers.ModelSerializer):
    room_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Topic
        fields = ["id", "topic_name", "creator", "room_count"]
        read_only_fields = ["creator", "room_count"]

    def validate(self, data):
        if self.instance and "topic_name" not in data:
            raise serializers.ValidationError("Topic name is required")
        return data


# Room Serializer
class RoomSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    # Accept topic as a string
    topic = serializers.CharField(write_only=True)
    # Use as output only (detailed topic object)
    topic_details = TopicSerializer(source="topic", read_only=True)

    class Meta:
        model = Room
        fields = ["id", "owner", "topic", "topic_details", "room_name",
                  "room_description", "participants", "created_at"]
        read_only_fields = ["id", "owner", "participants", "created_at"]

    def create(self, validated_data):
        owner = self.context["request"].user
        topic_name = validated_data.pop("topic").strip()
        if not topic_name:
            raise serializers.ValidationError(
                {"topic_input": "Topic name cannot be empty."})
        topic, _ = Topic.objects.get_or_create(
            topic_name=topic_name,
            defaults={"creator": owner}
        )
        validated_data["owner"] = owner
        validated_data["topic"] = topic
        room = super().create(validated_data)
        room.participants.add(owner)
        return room

    def validate(self, data):
        owner = self.context["request"].user
        if not data.get("topic"):
            raise serializers.ValidationError(
                {"topic_name": "Topic is required."})

        if self.instance and "topic" in data and data["topic"] is None:
            raise serializers.ValidationError(
                {"topic_name": "Topic is required when updating."})
        topic_name = data.pop("topic").strip()
        topic, _ = Topic.objects.get_or_create(
            topic_name=topic_name,
            defaults={"creator": owner}
        )
        data["topic"] = topic

        if "participants" in data:
            raise serializers.ValidationError(
                {"participants": "You are not allowed to modify participants directly"})

        if "owner" in data:
            raise serializers.ValidationError(
                {"owner": "You are not allowed to change the owner."})
        return data
