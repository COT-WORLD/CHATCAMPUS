from django.db.models.signals import post_migrate, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from chatcampusapp.tasks import invalidate_and_warm_all_cache
from chatcampusapp.models import Topic, Room, Message
from faker import Faker
from faker.providers import BaseProvider
import random
from decouple import config
import sys
from django.core.cache import cache
import logging
logger = logging.getLogger("chatcampusapp")

fake = Faker()
User = get_user_model()

TOPIC_NAMES = [
    "Artificial Intelligence", "Machine Learning", "Web Development", "APIs",
    "Cloud Computing", "Databases", "Cybersecurity", "DevOps", "Python", "JavaScript"
]

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ivan", "Jasmine"
]

class TechProvider(BaseProvider):
    tech_topics = [
        "technology", "programming", "software development", 
        "education", "cloud computing", "AI", "web development"
    ]
    
    def tech_sentence(self):
        topic = random.choice(self.tech_topics)
        return f"Experienced professional specializing in {topic} with a passion for innovation."

fake.add_provider(TechProvider)



@receiver(post_migrate)
def initialize_project_data(sender, **kwargs):
    if 'test' in sys.argv:
        logging.info("Skipping data seeding during test run.")
        return
    seed_initial_data()


def seed_initial_data():
    # Avoid reseeding if data exists
    if Room.objects.exists():
        return

    logging.info("🌱 Seeding users...")
    users = create_users()
    logging.info("🌱 Seeding topics...")
    topics = create_topics()
    logging.info("🏗 Creating rooms...")
    rooms = create_rooms(users, topics)
    logging.info("💬 Creating messages...")
    add_messages_and_participants(rooms, users)
    logging.info("✅ Seeding completed.")


def create_users():
    if not User.objects.filter(email=config("DJANGO_SUPER_USER_EMAIL")).exists():
        bio = fake.tech_sentence()
        User.objects.create_superuser(
            first_name=config("DJANGO_SUPER_USER_FIRSTNAME"),
            last_name=config("DJANGO_SUPER_USER_LASTNAME"),
            email=config("DJANGO_SUPER_USER_EMAIL"),
            password=config("DJANGO_SUPER_USER_PASSWORD"),
            bio=bio,
        )

    users = []
    for name in FIRST_NAMES:
        if not User.objects.filter(first_name=name.lower()).exists():
            bio = fake.tech_sentence()
            user = User.objects.create_user(
                first_name=name.lower(),
                last_name="smith",
                email=f"{name.lower()}@gmail.com",
                password="securepass123"
            )
            user.bio = bio
            user.save()
            users.append(user)
        else:
            users.append(User.objects.get(first_name=name.lower()))
    return users


def create_topics():
    topics_objs = [Topic(topic_name=name) for name in TOPIC_NAMES]
    Topic.objects.bulk_create(topics_objs, ignore_conflicts=True)
    return list(Topic.objects.all())


def create_rooms(users, topics):
    rooms = []
    for i, user in enumerate(users):
        topic = random.choice(topics)
        room = Room(
            owner=user,
            topic=topic,
            room_name=f"{topic.topic_name} Discussion {i}",
            room_description=f"Discussion on {topic.topic_name.lower()} and its applications.",
        )
        rooms.append(room)
    Room.objects.bulk_create(rooms)
    return list(Room.objects.all())


def add_messages_and_participants(rooms, users):
    through_model = Room.participants.through
    through_entries = []
    messages = []

    total_users_count = len(users)

    for room in rooms:
        available_potential_participants = [
            u for u in users if u != room.owner]
        num_available_potential_participants = len(
            available_potential_participants)

        max_participants_to_add = min(num_available_potential_participants, 10)

        if max_participants_to_add <= 0:
            num_other_partcipants = 0
        else:
            num_other_partcipants = random.randint(1, max_participants_to_add)

        other_participants = random.sample(
            available_potential_participants,
            k=num_other_partcipants
        )
        participants = set([room.owner])
        participants.update(other_participants)

        host_message = fake.tech_sentence()
        messages.append(
            Message(owner=room.owner, room=room, body=host_message)
        )
        through_entries.append(
            through_model(user_id=room.owner.id, room_id=room.id)
        )

        for participant in other_participants:
            through_entries.append(
                through_model(user_id=participant.id, room_id=room.id)
            )
            num_messages = random.randint(1, 3)

            for _ in range(num_messages):
                message_body = fake.tech_sentence()
                messages.append(
                    Message(owner=participant,
                            room_id=room.id, body=message_body)
                )

    through_model.objects.bulk_create(through_entries, ignore_conflicts=True)
    Message.objects.bulk_create(messages)


@receiver([post_save], sender=Room)
@receiver([post_save], sender=Message)
@receiver([post_save], sender=User)
@receiver([post_save], sender=Topic)
def handle_model_change_invalidate_all_cache(sender, instance, **kwargs):
    logger.info("Signal triggered; warming cache.")
    invalidate_and_warm_all_cache.delay()
    logger.info("Warming cache finished.")


@receiver(post_delete, sender=Room)
def handle_room_delete(sender, instance, **kwargs):
    logger.info(f"Room deleted: {instance.id}")
    invalidate_and_warm_all_cache.delay({"model": "Room", "id": instance.id})


@receiver(post_delete, sender=User)
def handle_user_delete(sender, instance, **kwargs):
    logger.info(f"User deleted: {instance.id}")
    invalidate_and_warm_all_cache.delay({"model": "User", "id": instance.id})


@receiver(post_delete, sender=Message)
def handle_generic_delete(sender, instance, **kwargs):
    logger.info(f"{sender.__name__} deleted: {instance.id}")
    invalidate_and_warm_all_cache.delay()
