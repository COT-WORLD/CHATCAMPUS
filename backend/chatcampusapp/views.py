from django.db import connection
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
from django.core.cache import cache
from .tasks import warm_up_dashboard_view_cache, warm_up_room_detail_view_cache, warm_up_user_profile_view_cache
import time
import logging
logger = logging.getLogger("dashboard")
# Get logged in User
User = get_user_model()


# Register custom User and it's public route
class UserCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
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
        data = cache.get(f"RoomID{pk}")
        if not data:
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
            data = {
                "message": "Room details retrieve successfully",
                "room": RoomProfileSerializer(room, context={"request": request}).data,
                "messages": MessageProfileSerializer(messages, many=True, context={"request": request}).data,
                "participants": UserMinimalSerializer(participants, many=True, context={"request": request}).data
            }
            warm_up_room_detail_view_cache.delay(pk)
        return Response(data, status=status.HTTP_200_OK)

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

    def get_queryset_data(self, q, request):
        rooms = (Room.objects
                 .filter(Q(topic__topic_name__icontains=q) |
                         Q(room_name__icontains=q) |
                         Q(room_description__icontains=q))
                 .select_related("topic", "owner")
                 .annotate(participants_count=Count("participants",
                                                    # optional
                                                    filter=Q(participants__is_active=True)))
                 .only("id", "room_name", "created_at",
                       "topic__id", "topic__topic_name",
                       "owner__id", "owner__first_name", "owner__avatar")[:10])

        messages = Message.objects.filter(
            Q(room__topic__topic_name__icontains=q)
        ).select_related("owner", "room").only("id", "body", "created_at",
                                               "room__id", "room__room_name",
                                               "owner__id", "owner__first_name", "owner__avatar")[:10]

        all_topics = list(
            Topic.objects.annotate(room_count=Count(
                "room_topic")).order_by("-room_count")
        )
        topics = all_topics[:5]
        return {
            "message": "Homepage details retrieved successfully.",
            "rooms": RoomMinimalSerializer(rooms, many=True, context={"request": request}).data,
            "topics": TopicSerializer(topics, many=True).data,
            "topics_count": len(all_topics),
            "room_messages": MessageMinimalSerializer(messages, many=True, context={"request": request}).data,
        }

    def get(self, request):
        t0 = time.perf_counter()
        q = request.GET.get("q", "").strip()
        cache_key = f'homepage_cache_{q}' if q else 'homepage_cache'

        data = cache.get(cache_key)

        if not data:
            data = self.get_queryset_data(q, request)
            warm_up_dashboard_view_cache.delay(q)
        logger.info("Dashboard prod %.0f ms | queries %d",
                    (time.perf_counter()-t0)*1000, len(connection.queries))
        return Response(data, status=status.HTTP_200_OK)


# UserProfile
class UserProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        t0 = time.perf_counter()
        pk = kwargs["pk"]
        data = cache.get(f"UserID{pk}")
        if not data:
            if not pk:
                return Response({
                    "message": "User ID is required to get user profile."
                }, status=status.HTTP_400_BAD_REQUEST)
            user = get_object_or_404(
                User.objects.only('id', 'avatar', "first_name"), id=pk)
            rooms = (Room.objects
                     .filter(owner=user)
                     .select_related("topic", "owner")          # 1 query
                     .annotate(participants_count=Count("participants")).only("id", "room_name", "room_description", "created_at",
                                                                              "topic__id", "topic__topic_name",
                                                                              "owner__id", "owner__first_name", "owner__avatar")[:10])
            messages = (Message.objects
                        .filter(owner=user)
                        .select_related("room", "owner")
                        .only("id", "body", "created_at",
                              "room__id", "room__room_name",
                              "owner__id", "owner__first_name", "owner__avatar")[:8])
            all_topics = (Topic.objects
                          .annotate(room_count=Count("room_topic"))
                          .order_by("-room_count"))
            topics_count = len(all_topics)
            topics = all_topics[:5]
            data = {
                "message": "User profile retrieve successfully",
                "user": UserMinimalSerializer(user, context={"request": request}).data,
                "rooms": RoomMinimalSerializer(rooms, many=True, context={"request": request}).data,
                "room_messages": MessageMinimalSerializer(messages, many=True, context={"request": request}).data,
                "topics": TopicSerializer(topics, many=True).data,
                "topics_count": topics_count,
            }
            warm_up_user_profile_view_cache.delay(pk)
        logger.info("UserProfile prod %.0f ms | queries %d",
                    (time.perf_counter()-t0)*1000, len(connection.queries))
        return Response(data, status=status.HTTP_200_OK)


# CustomConvertToken
class GoogleAuthAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({"error": "No access token provided."}, status=400)

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

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'first_name': first_name, 'last_name': last_name}
        )

        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": user.email,
            "first_name": user.first_name,
        })
