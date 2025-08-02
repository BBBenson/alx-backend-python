# messaging/models.py

"""
Django models for messaging system
"""

import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(
        self, email, first_name, last_name, role, password=None, **extra_fields
    ):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser and uses UUID as primary key"""

    ROLE_CHOICES = [
        ("guest", "Guest"),
        ("host", "Host"),
        ("admin", "Admin"),
    ]

    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    first_name = models.CharField(max_length=151, null=False)
    last_name = models.CharField(max_length=151, null=False)
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=False)
    created_at = models.DateField(default=timezone.now)

    # Set authentication fields
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class Conversation(models.Model):
    """Representation of a conversation between two or more users"""

    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class UnreadMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(read=False)


class Message(models.Model):
    """Representation of a message sent by a user in a conversation

    Fields:
        - sender: The user who sent the message
        - receiver: The user who will receive the message (direct message recipient)
        - conversation: The conversation this message belongs to
        - content: The actual message content
        - timestamp: When the message was sent
        - read: Whether the message has been read by the receiver
        - is_thread: Whether this message has replies
        - parent_message: Reference to the parent message if this is a reply
    """

    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages", null=False
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages", null=False
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages", null=False
    )
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
        db_index=True,
    )
    content = models.TextField(null=False, verbose_name="message body")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="sent at")
    edited = models.BooleanField(default=False)
    read = models.BooleanField(
        default=False, db_index=True, verbose_name="message read"
    )
    is_thread = models.BooleanField(
        default=False, help_text="Whether this message is a thread starter"
    )

    # Custom managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["conversation", "parent_message"]),
        ]

    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Check if the message is being updated (has an ID) and content has changed
        if self.pk and self.content != self.__class__.objects.get(pk=self.pk).content:
            self.edited = True
        super().save(*args, **kwargs)

        # If this is a reply, mark the parent as a thread
        if self.parent_message and not self.parent_message.is_thread:
            self.parent_message.is_thread = True
            self.parent_message.save(update_fields=["is_thread"])

        super().save(*args, **kwargs)

    def get_thread(self, include_self=True):
        """
        Get all messages in this thread (all replies to the same parent)
        """
        if self.parent_message:
            # If this is a reply, get all messages in the same thread
            thread_messages = Message.objects.filter(
                parent_message=self.parent_message
            ).select_related("sender", "receiver")
        else:
            # If this is a thread starter, get all its replies
            thread_messages = Message.objects.filter(
                parent_message=self
            ).select_related("sender", "receiver")

        if include_self and not self.parent_message:
            # If this is a thread starter, include it in the results
            thread_messages = list(thread_messages)
            thread_messages.insert(0, self)

        return thread_messages

    def get_thread_depth(self):
        """
        Calculate the depth of this message in a thread
        """
        depth = 0
        current = self
        while current.parent_message:
            depth += 1
            current = current.parent_message
        return depth


class MessageHistory(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="history"
    )
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-edited_at"]
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return (
            f"Edit of {self.message.message_id} by {self.edited_by} at {self.edited_at}"
        )


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="notifications"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user} - {self.message.content[:30]}..."
