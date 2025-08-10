# chats/management/commands/create_test_data.py
from datetime import datetime, timedelta

from chats.models import Conversation, Message
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Creates test users and conversations"

    def handle(self, *args, **options):
        # Create test users
        kwame = User.objects.create_user(
            username="kwame",
            email="kwame@example.com",
            first_name="Kwame",
            last_name="Mensah",
            password="testpass123",
            role="user",
        )

        ama = User.objects.create_user(
            username="ama",
            email="ama@example.com",
            first_name="Ama",
            last_name="Agyei",
            password="testpass123",
            role="user",
        )

        kofi = User.objects.create_user(
            username="kofi",
            email="kofi@example.com",
            password="testpass123",
            first_name="Kofi",
            last_name="Asante",
            role="user",
        )

        # Create a conversation between Kwame and Ama
        convo = Conversation.objects.create()
        convo.participants.add(kwame, ama)

        # Add some test messages
        messages = [
            (kwame, "Ama! Ɛte sɛn?"),
            (ama, "Meho da ase. Wo nso te sɛn?"),
            (kwame, "Menso meho yɛ."),
            (ama, "Yɛbɛhyia ɔkyena wɔ adwumayɛbea no mu."),
            (kwame, "Ɛyɛ, yɛbɛhyia kɔkɔɔ."),
        ]

        for i, (sender, text) in enumerate(messages):
            Message.objects.create(
                sender=sender,
                conversation=convo,
                message_body=text,
                sent_at=datetime.now() - timedelta(minutes=len(messages) - i),
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created test data:\n"
                f"- Users: {kwame.username}, {ama.username}, {kofi.username}\n"
                f"- Conversation between {kwame.first_name} and {ama.first_name}\n"
                f"- {len(messages)} test messages"
            )
        )
