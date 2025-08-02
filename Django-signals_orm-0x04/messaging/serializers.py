# messaging/serializers.py

"""
Serializers for User, Conversation, and Message models
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    user_id = serializers.UUIDField(source="id", read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    phone_number = serializers.CharField(allow_blank=True, required=False)
    role = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create and return a new user with encrypted password"""
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly if provided"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include user data in the token response
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user:
            raise serializers.ValidationError("User not found")
        refresh = self.get_token(self.user)

        # Add custom claims
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["user"] = UserSerializer(self.user).data

        return data


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""

    message_id = serializers.UUIDField(source="id", read_only=True)
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    content = serializers.CharField(source="message_body")
    timestamp = serializers.DateTimeField(source="sent_at", read_only=True)
    is_thread = serializers.BooleanField(read_only=True)
    thread_depth = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "receiver",
            "content",
            "timestamp",
            "is_thread",
            "thread_depth",
            "reply_count",
            "parent_message",
        ]
        read_only_fields = [
            "message_id",
            "timestamp",
            "sender",
            "receiver",
            "is_thread",
            "thread_depth",
            "reply_count",
        ]

    def get_thread_depth(self, obj):
        return obj.get_thread_depth()

    def get_reply_count(self, obj):
        return obj.replies.count() if hasattr(obj, "replies") else 0


class ConversationListSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(source="id", read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["conversation_id", "participants", "created_at", "last_message"]
        read_only_fields = ["conversation_id", "created_at"]

    def get_last_message(self, obj):
        last_message = obj.messages.order_by("-sent_at").first()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested participants and messages"""

    conversation_id = serializers.UUIDField(source="id", read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    # Field for writing participants (using IDs)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True, source="participants"
    )

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "created_at",
            "messages",
        ]
        read_only_fields = ["conversation_id", "created_at", "messages"]

    def validate_participant_ids(self, value):
        """Ensure at least 2 participants in a conversation"""
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants."
            )
        return value
