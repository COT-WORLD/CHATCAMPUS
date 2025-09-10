import time
from celery import shared_task
from django.core.cache import cache
from django.http import Http404
from .models import User, Topic, Room, Message
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .serializers import RoomProfileSerializer, MessageProfileSerializer, UserMinimalSerializer, RoomMinimalSerializer, MessageMinimalSerializer, TopicSerializer, RoomSerializer, MessageSerializer
from chatcampusapp.utils.redis_tracking import track_used_query, track_used_room_id, track_used_user_id
from django_redis import get_redis_connection

import logging

logger = logging.getLogger("chatcampusapp")


def should_warm_dashboard_cache(q):
    key = f'dashboard_last_updated_{q}'
    last_updated = cache.get(key)
    now = time.time()
    if last_updated and now - last_updated < 10:
        return False
    cache.set(key, now, timeout=300)
    return True


@shared_task
def warm_up_room_detail_view_cache(room_id):
    try:
        room = get_object_or_404(
            Room.objects.select_related(
                "topic", "owner").prefetch_related("participants"), id=room_id
        )
        messages = room.room_message.select_related(
            "owner").order_by("created_at")
        participants = room.participants.all()
        data = {
            "message": "Room details retrieve successfully",
            "room": RoomProfileSerializer(room).data,
            "messages": MessageProfileSerializer(messages, many=True).data,
            "participants": UserMinimalSerializer(participants, many=True).data
        }
        cache.set(f"RoomID{room_id}", data, timeout=300)
        track_used_room_id(room_id)
    except Room.DoesNotExist:
        logging.error("Room does not exist")
    except Http404:
        logger.warning(f"Room {room_id} resulted in 404. Skipping.")


@shared_task
def warm_up_dashboard_view_cache(q):
    if not should_warm_dashboard_cache(q):
        logger.info(
            f"Skipped warming cache for query '{q}' as it was updated recently.")
        return
    try:
        rooms = Room.objects.filter(
            Q(topic__topic_name__icontains=q) |
            Q(room_name__icontains=q) |
            Q(room_description__icontains=q)
        ).select_related("topic").only("id", "room_name", "room_description", "topic")[:10]

        messages = Message.objects.filter(
            Q(room__topic__topic_name__icontains=q)
        ).select_related("owner", "room").only("id", "body", "room_id", "owner_id", "created_at")[:10]

        all_topics = list(
            Topic.objects.annotate(room_count=Count(
                "room_topic")).order_by("-room_count")
        )
        topics = all_topics[:5]

        data = {
            "message": "Homepage details retrieved successfully.",
            "rooms": RoomMinimalSerializer(rooms, many=True).data,
            "topics": TopicSerializer(topics, many=True).data,
            "topics_count": len(all_topics),
            "room_messages": MessageMinimalSerializer(messages, many=True).data,
        }

        cache_key = f'homepage_cache_{q}' if q else 'homepage_cache'
        cache.set(cache_key, data, timeout=300)
        track_used_query(q)

    except Exception as e:
        logger.error(f"Error in warm_up_dashboard_view_cache: {e}")


@shared_task
def warm_up_user_profile_view_cache(user_id):
    try:
        user_details = get_object_or_404(
            User.objects.prefetch_related('room_owner', 'message_owner'), id=user_id)
        rooms = user_details.room_owner.all().select_related('topic')
        messages = user_details.message_owner.all(
        ).select_related('room')[:8]
        all_topics = list(Topic.objects.annotate(room_count=Count(
            "room_topic")).order_by("-room_count"))
        topics_count = len(all_topics)
        topics = all_topics[:5]
        data = {
            "message": "User profile retrieve successfully",
            "user": UserMinimalSerializer(user_details).data,
            "rooms": RoomSerializer(rooms, many=True).data,
            "room_messages": MessageSerializer(messages, many=True).data,
            "topics": TopicSerializer(topics, many=True).data,
            "topics_count": topics_count,
        }
        cache.set(f"UserID{user_id}", data, 300)
        track_used_user_id(user_id)
    except User.DoesNotExist:
        logging.error("User does not exist")


@shared_task
def invalidate_and_warm_all_cache(payload=None):
    redis = get_redis_connection("default")

    cache.delete("homepage_cache")
    q_keys = redis.smembers("homepage_q_keys") or set()

    pipe = redis.pipeline()
    for q in q_keys:
        q = q.decode() if isinstance(q, bytes) else q
        pipe.delete(f"homepage_cache_{q}")
    pipe.execute()

    for q in q_keys:
        q = q.decode() if isinstance(q, bytes) else q
        warm_up_dashboard_view_cache.delay(q)

    warm_up_dashboard_view_cache.delay("")

    model = payload.get("model") if payload else None
    object_id = payload.get("id") if payload else None

    if model == "Room" and object_id:
        pipe = redis.pipeline()
        pipe.delete(f"RoomID{object_id}")
        pipe.srem("room_ids_used", str(object_id))
        pipe.execute()
        logger.info(f"Deleted RoomID{object_id} from cache.")
        return

    if model == "User" and object_id:
        pipe = redis.pipeline()
        pipe.delete(f"UserID{object_id}")
        pipe.srem("user_ids_used", str(object_id))
        pipe.execute()
        logger.info(f"Deleted UserID{object_id} from cache.")
        return

    room_ids = redis.smembers("room_ids_used") or set()
    for room_id in room_ids:
        rid = int(room_id.decode())
        warm_up_room_detail_view_cache.delay(rid)

    user_ids = redis.smembers("user_ids_used") or set()
    for user_id in user_ids:
        uid = int(user_id.decode())
        warm_up_user_profile_view_cache.delay(uid)
