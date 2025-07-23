from functools import partial
from multiprocessing import context
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .serializers import RoomSerializer, TopicSerializer, UserSerializer
from .models import Room, Topic
from django.db.models import Count

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
                "message": "User created successfully",
                "user": UserSerializer(user, context={'request': request}).data
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
class RoomTopicCreateUpdateRetrieveDeleteListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        """
        GET:
        - If `pk` is provided: retrieve a single room.
        - Else: list all rooms for the current user.
        """
        if pk:
            room = get_object_or_404(Room, pk=pk)
            serializer = RoomSerializer(room)
            return Response({
                "message": "Room retrieve successfully",
                "room": serializer.data
            }, status=status.HTTP_200_OK)
        # list all rooms
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response({
            "message": "Rooms retrieve successfully",
            "room": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new room.
        """
        print(request.data)
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

    def patch(self, request, pk=None):
        """
        Partially update an existing room.
        Only the owner can update the room.
        """
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

    def delete(self, request, pk=None):
        """
        Delete a room.
        """
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


class TopicListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = self.request.GET.get("q", "")
        if q:
            topics = Topic.objects.filter(name__icontains=q).annotate(
                room_count=Count('room_topic')).order_by('-room_count')
        else:
            topics = Topic.objects.all().annotate(room_count=Count('room_topic'))
        serializer = TopicSerializer(topics, many=True)
        print(serializer.data)
        return Response({
            "message": "Topic retrieve suceessfully",
            "topic": serializer.data
        }, status=status.HTTP_200_OK)
