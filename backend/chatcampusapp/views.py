from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .serializers import MessageMinimalSerializer, MessageProfileSerializer, MessageSerializer, RoomMinimalSerializer, RoomProfileSerializer, RoomSerializer, TopicSerializer, UserMinimalSerializer, UserSerializer
from .models import Message, Room, Topic
from django.db.models import Count, Q
import bleach
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from decouple import config

# Get logged in User
User = get_user_model()


# Register custom User and it's public route
class UserCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "User registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Retrieve loggedin user and update their profile
class UserRetrieveUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            "message": "User profile retrieve successfully",
            "user": serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "User profile updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Profile update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Create Room and Topic create, list, get, update and delete
class RoomUpdateRetrieveDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        GET:
        - If `pk` is provided: retrieve a single room.
        """
        pk = kwargs["pk"]
        if pk:
            room = get_object_or_404(Room, pk=pk)
            serializer = RoomSerializer(room)
            return Response({
                "message": "Room retrieve successfully",
                "room": serializer.data
            }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Partially update an existing room.
        Only the owner can update the room.
        """
        pk = kwargs["pk"]
        if not pk:
            return Response({
                "message": "Room ID is required for the update."
            }, status=status.HTTP_400_BAD_REQUEST)

        room = get_object_or_404(Room, pk=pk)

        if room.owner != request.user:
            return Response({
                "message": "Unauthorised to update this room."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = RoomSerializer(
            room, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Room updated successfully",
                "room": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "message": "Room update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Delete a room.
        """
        pk = kwargs["pk"]
        if not pk:
            return Response({
                "message": "Room ID is required for delete."
            }, status=status.HTTP_400_BAD_REQUEST)

        room = get_object_or_404(Room, pk=pk)

        if room.owner != request.user:
            return Response({
                "message": "Unauthorised to delete this room."
            }, status=status.HTTP_403_FORBIDDEN)

        room.delete()
        return Response({
            "message": "Room deleted suceessfully"
        }, status=status.HTTP_204_NO_CONTENT)


class RoomCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Create a new room.
        """
        serializer = RoomSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Room created successfully",
                "room": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Room creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Topic list
class TopicListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = self.request.GET.get("q", "")
        if q:
            topics = Topic.objects.filter(topic_name__icontains=q).annotate(
                room_count=Count('room_topic')).order_by('-room_count', 'topic_name')
        else:
            topics = Topic.objects.all().annotate(
                room_count=Count('room_topic')).order_by('-room_count', 'topic_name')
        serializer = TopicSerializer(topics, many=True)
        return Response({
            "message": "Topics retrieve successfully",
            "topics": serializer.data
        }, status=status.HTTP_200_OK)


# Room details and Message create and delete
class RoomDetailMessageCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        if not pk:
            return Response({
                "message": "Room ID is required to get room details."
            }, status=status.HTTP_400_BAD_REQUEST)
        room = get_object_or_404(
            Room.objects.select_related(
                "topic", "owner").prefetch_related("participants"), id=pk
        )
        messages = room.room_message.select_related(
            "owner").order_by("created_at")
        participants = room.participants.all()

        return Response({
            "message": "Room details retrieve successfully",
            "room": RoomProfileSerializer(room, context={"request": request}).data,
            "messages": MessageProfileSerializer(messages, many=True, context={"request": request}).data,
            "participants": UserMinimalSerializer(participants, many=True, context={"request": request}).data,
            "message_count": messages.count()
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        if not pk:
            return Response({
                "message": "Message ID is required to create message."
            }, status=status.HTTP_400_BAD_REQUEST)
        room = get_object_or_404(Room, id=pk)
        user = request.user
        body = request.data.get("body", "").strip()
        if not body:
            return Response({
                "message": "Message body is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # sanitize input

        allowed_tags = ['p', 'b', 'i', 'ul', 'ol', 'li', 'a', 'strong', 'em']
        allowed_attrs = {'a': ['href', 'title', 'rel']}
        clean_body = bleach.clean(
            body, tags=allowed_tags, attributes=allowed_attrs)

        message = Message.objects.create(
            owner=user, room=room, body=clean_body)

        room.participants.add(user)

        return Response({
            "message": "Message created successfully",
            "messages": MessageSerializer(message).data
        }, status=status.HTTP_201_CREATED)


# Message delete
class MessageDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """
        Delete a message.
        """
        pk = kwargs["pk"]
        if not pk:
            return Response({
                "message": "Message Id is required to delete."
            }, status=status.HTTP_400_BAD_REQUEST)

        message = get_object_or_404(Message, pk=pk)

        if request.user != message.owner:
            return Response({
                "message": "Unauthorised to delete message."
            }, status=status.HTTP_403_FORBIDDEN)

        message.delete()
        return Response({
            "message": "Message deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)


# Homepage details
class HomePageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.GET.get("q", "").strip()

        rooms = Room.objects.filter(
            Q(topic__topic_name__icontains=q) |
            Q(room_name__icontains=q) |
            Q(room_description__icontains=q)
        ).select_related("topic").only("id", "room_name", "room_description", "topic")[0:10]

        topics = (Topic.objects.annotate(room_count=Count(
            "room_topic")).order_by("-room_count")[0:5])

        messages = Message.objects.filter(
            Q(room__topic__topic_name__icontains=q)
        ).select_related("owner", "room").only("id", "body", "room_id", "owner_id", "created_at")[0:10]

        return Response({
            "message": "Homepage detials retrieve successfully.",
            "rooms": RoomMinimalSerializer(rooms, many=True, context={"request": request}).data,
            "topics": TopicSerializer(topics, many=True).data,
            "topics_count": Topic.objects.count(),
            "room_messages": MessageMinimalSerializer(messages, many=True, context={"request": request}).data,
        }, status=status.HTTP_200_OK)


# UserProfile
class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        if not pk:
            return Response({
                "message": "User ID is required to get user profile."
            }, status=status.HTTP_400_BAD_REQUEST)
        user_details = get_object_or_404(User, id=pk)
        rooms = user_details.room_owner.all()
        messages = user_details.message_owner.all()[:8]
        topics = Topic.objects.annotate(room_count=Count(
            "room_topic")).order_by("-room_count")[:5]

        return Response({
            "message": "User profile retrieve successfully",
            "user": UserMinimalSerializer(user_details, context={"request": request}).data,
            "rooms": RoomSerializer(rooms, many=True, context={"request": request}).data,
            "room_messages": MessageSerializer(messages, many=True, context={"request": request}).data,
            "topics": TopicSerializer(topics, many=True).data,
            "topics_count": Topic.objects.count(),
        }, status=status.HTTP_200_OK)


# CustomConvertToken
class GoogleAuthAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({"error": "No access token provided."}, status=400)

        # 1. Get user info from Google
        userinfo_url = f"{config("GOOGLE_AUTH_URI")}{access_token}"
        resp = requests.get(userinfo_url)
        if resp.status_code != 200:
            return Response({"error": "Could not retrieve user info from Google"}, status=400)

        user_data = resp.json()
        email = user_data.get('email')
        first_name = user_data.get('given_name', '')
        last_name = user_data.get('family_name', '')

        if not email:
            return Response({"error": "Google account has no email"}, status=400)

        # 2. Create or fetch user in your DB
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'first_name': first_name, 'last_name': last_name}
        )
        # (Optional: update names on each login)
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # 3. Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": user.email,
            "first_name": user.first_name,
        })
