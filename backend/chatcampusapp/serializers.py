from urllib.parse import urlparse
from rest_framework import serializers
from .models import User
from PIL import Image


# Custom User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email",
                  "password", "avatar", "bio", "last_login"]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "avatar": {"required": False, "allow_null": True},
        }

    # validate first name
    def validate_first_name(self, value):
        if '<' in value or '>' in value:
            raise serializers.ValidationError("Bio cannot contain HTML.")
        return value

    # validate last name
    def validate_last_name(self, value):
        if '<' in value or '>' in value:
            raise serializers.ValidationError("Bio cannot contain HTML.")
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
