# messaging/management/commands/create_test_data.py

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from messaging.models import Conversation, Message

User = get_user_model()


class Command(BaseCommand):
    help = "Creates test users and conversations"

    def handle(self, *args, **options):
        # Clear existing test data to avoid duplicates
        self.stdout.write("Cleaning up existing test data...")
        User.objects.filter(username__in=["kwame", "ama", "kofi"]).delete()

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

        # Add some test messages with proper timezone-aware timestamps
        messages_data = [
            (kwame, "Ama! Ɛte sɛn?"),
            (ama, "Meho da ase. Wo nso te sɛn?"),
            (kwame, "Menso meho yɛ."),
            (ama, "Yɛbɛhyia ɔkyena wɔ adwumayɛbea no mu."),
            (kwame, "Ɛyɛ, yɛbɛhyia kɔkɔɔ."),
        ]

        # Create messages with properly spaced timestamps
        base_time = timezone.now() - timedelta(hours=1)

        for i, (sender, text) in enumerate(messages_data):
            # Create message instance without triggering the problematic save logic
            message = Message(
                sender=sender,
                conversation=convo,
                content=text,
                timestamp=base_time + timedelta(minutes=i * 5),  # 5 minutes apart
            )

            # Save the message (this will trigger your custom save method)
            try:
                message.save()
                self.stdout.write(f"Created message: {text[:30]}...")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating message '{text}': {e}")
                )
                continue

        # Create an additional conversation with all three users
        group_convo = Conversation.objects.create()
        group_convo.participants.add(kwame, ama, kofi)

        # Add a group message
        group_message = Message(
            sender=kofi,
            conversation=group_convo,
            content="Mo nyina ɛte sɛn? (How is everyone?)",
            timestamp=timezone.now(),
        )

        try:
            group_message.save()
            self.stdout.write("Created group conversation message")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating group message: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created test data:\n"
                f"- Users: {kwame.username}, {ama.username}, {kofi.username}\n"
                f"- Conversation between {kwame.first_name} and {ama.first_name}\n"
                f"- Group conversation with all three users\n"
                f"- {len(messages_data) + 1} test messages"
            )
        )
