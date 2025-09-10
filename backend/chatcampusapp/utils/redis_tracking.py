from django_redis import get_redis_connection

TTL_SECONDS = 300


def track_used_room_id(room_id):
    redis = get_redis_connection("default")
    redis.sadd("room_ids_used", room_id)
    redis.expire("room_ids_used", TTL_SECONDS)


def track_used_user_id(user_id):
    redis = get_redis_connection("default")
    redis.sadd("user_ids_used", user_id)
    redis.expire("user_ids_used", TTL_SECONDS)


def track_used_query(q):
    redis = get_redis_connection("default")
    redis.sadd("homepage_q_keys", q)
    redis.expire("homepage_q_keys", TTL_SECONDS)
