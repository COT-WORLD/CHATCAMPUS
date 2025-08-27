from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Message, Room
from .serializers import MessageSerializer
from django.shortcuts import get_object_or_404
import bleach
from django.http import Http404
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache


@database_sync_to_async
def get_message_by_id(message_id):
    return Message.objects.select_related('owner').get(id=message_id)


@database_sync_to_async
def delete_message_instance(message):
    message.delete()


@database_sync_to_async
def get_room_by_id(pk):
    return get_object_or_404(Room, id=pk)


@database_sync_to_async
def create_message(user, room, body):
    clean_body = bleach.clean(
        body,
        tags=["p", "b", "i", "ol", "li", "a", "strong", "em"],
        attributes={'a': ["href", "title", "rel"]}
    )
    message = Message.objects.create(owner=user, room=room, body=clean_body)
    room.participants.add(user)
    return message


@database_sync_to_async
def serialize_message_to_dict(message):
    return MessageSerializer(message).data


@database_sync_to_async
def validate_token_and_get_user(token):
    jwt_auth = JWTAuthentication()
    validated_token = jwt_auth.get_validated_token(token)
    user = jwt_auth.get_user(validated_token)
    return user


class ChatRoom(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["id"]
        self.room_group_name = f"ChatRoom_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': "You are now connected!"
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "Auth_Check":
            token = data.get("token")
            try:
                user = await validate_token_and_get_user(token)
            except Exception:
                await self.close()
                return
            if not user or not user.is_authenticated:
                await self.close()
                return

            self.scope['user'] = user  # Mark connection authenticated
            await self.send(text_data=json.dumps({
                "type": "auth_success",
                "message": "Authentication successful"
            }))
            return

        # From here on, user must be authenticated
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return

        if action == "send_message":
            room_id = self.room_id
            body = data.get("body")
            try:
                room = await get_room_by_id(room_id)
            except Http404:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Room not found"
                }))
                return
            try:
                message = await create_message(user, room, body)
                cache.delete(f"RoomID{self.room_id}")
                cache.delete("homepage_cache")
                cache.delete(f"UserID{user.id}")
                serialized_message = await serialize_message_to_dict(message)
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "chat_message",
                    "message": serialized_message
                })
            except Exception as e:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": str(e)
                }))

        elif action == "delete_message":
            message_id = data.get("message_id")
            try:
                message = await get_message_by_id(message_id)
                if message.owner != user:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "Unauthorized to delete this message."
                    }))
                    return
                await delete_message_instance(message)
                cache.delete(f"RoomID{self.room_id}")
                cache.delete("homepage_cache")
                cache.delete(f"UserID{user.id}")
                await self.channel_layer.group_send(self.room_group_name, {
                    "type": "chat_message_delete",
                    "message_id": message_id,
                })
            except Message.DoesNotExist:
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Message not found"
                }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"]
        }))

    async def chat_message_delete(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message_delete",
            "message_id": event["message_id"]
        }))
