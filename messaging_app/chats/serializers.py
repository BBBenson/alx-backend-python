from rest_framework import serializers
from .models import User, Conversation, Message


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'phone_number',
        ]


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'message_body',
            'sent_at',
        ]


# Conversation Serializer with nested messages
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages',
            'created_at',
        ]

    def get_messages(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data

    def validate(self, attrs):
        """
        Example of validation: Ensure at least 2 participants in a conversation
        """
        participants = attrs.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError("A conversation must have at least two participants.")
        return attrs
