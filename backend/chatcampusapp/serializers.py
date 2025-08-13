from urllib.parse import urlparse
from rest_framework import serializers
from .models import Message, Room, Topic, User
from PIL import Image
import re
import bleach


# Custom User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email",
                  "password", "avatar", "bio", "last_login"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "avatar": {"required": False, "allow_null": True},
        }

    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value)
        if self.instance:
            user = user.exclude(pk=self.instance.pk)
        if user.exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

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
                image.verify()
                value.file.seek(0)
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
        fields = ["id", "topic_name", "room_count"]
        read_only_fields = ["room_count"]

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
        topic_value = validated_data.pop("topic")
        if isinstance(topic_value, str):
            topic_name = topic_value.strip()
            if not topic_name:
                raise serializers.ValidationError(
                    {"topic": "Topic name cannot be empty."})
            topic, _ = Topic.objects.get_or_create(
                topic_name=topic_name,
                defaults={"creator": owner}
            )
        elif isinstance(topic_value, Topic):
            topic = topic_value
        else:
            raise serializers.ValidationError({"topic": "Invalid topic input"})

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
        )
        data["topic"] = topic

        if "participants" in data:
            raise serializers.ValidationError(
                {"participants": "You are not allowed to modify participants directly"})

        if "owner" in data:
            raise serializers.ValidationError(
                {"owner": "You are not allowed to change the owner."})
        return data


# Message serializer
class MessageSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    room_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ["id", "owner", "room", "room_id", "body", "created_at"]
        read_only_fields = ["id", "owner", "room", "created_at"]

    def create(self, validated_data):
        owner = self.context["request"].user
        room_id = validated_data.pop("room_id")
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError(
                {"room_id": "Room does not exist."})

        return Message.objects.create(
            owner=owner,
            room=room,
            body=validated_data["body"]
        )

    def validate_body(self, value):
        impersonation_pattern = r"\{[a-zA-Z0-9_]+\}"

        if re.search(impersonation_pattern, value):
            raise serializers.ValidationError(
                "Message contains impersonation pattern.")
        return bleach.clean(value, tags=[], strip=True)


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'avatar', 'first_name']


class TopicNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["topic_name"]


class RoomMinimalSerializer(serializers.ModelSerializer):
    owner = UserMinimalSerializer(read_only=True)
    participants_count = serializers.SerializerMethodField()
    topic_details = TopicNameSerializer(source="topic", read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'owner', 'created_at',
                  'participants_count', 'topic_details']

    def get_participants_count(self, obj):
        return obj.participants.count()


class RoomNameandIDSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_name']


class MessageMinimalSerializer(serializers.ModelSerializer):
    owner = UserMinimalSerializer(read_only=True)
    room = RoomNameandIDSerilizer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'body', 'created_at', 'owner', 'room']
        read_only_fields = ['id', 'owner', 'room', 'created_at']


class RoomProfileSerializer(serializers.ModelSerializer):
    owner = UserMinimalSerializer(read_only=True)
    topic_details = TopicNameSerializer(source="topic", read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'room_description',
                  'owner', 'created_at', 'topic_details']


class MessageProfileSerializer(serializers.ModelSerializer):
    owner = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'body', 'created_at', 'owner']
        read_only_fields = ['id', 'owner', 'created_at']
