# messaging/tests.py

from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Conversation, Message, Notification

User = get_user_model()


class NotificationSignalTests(TestCase):
    def setUp(self):
        # Create users
        self.sender = User.objects.create_user(
            username="sender", email="sender@example.com", password="testpass123"
        )
        self.receiver = User.objects.create_user(
            username="receiver", email="receiver@example.com", password="testpass123"
        )

        # Create a conversation
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.sender, self.receiver)

    def test_notification_created_on_message_save(self):
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            conversation=self.conversation,
            content="Test message",
        )

        # Check if notification was created
        notification_exists = Notification.objects.filter(
            user=self.receiver, message=message
        ).exists()

        self.assertTrue(
            notification_exists,
            "Notification should be created when a new message is sent",
        )
