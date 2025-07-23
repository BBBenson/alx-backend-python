from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwnerOrParticipant


# Conversation filters
class ConversationFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Conversation
        fields = ['created_at']


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversations.
    Only authenticated users who are participants can access.
    """
    serializer_class = ConversationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ConversationFilter
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrParticipant]

    def get_queryset(self):
        # Only conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a conversation with participants.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create conversation
        conversation = Conversation.objects.create()
        participants_data = request.data.get('participants', [])

        # Add current user if not already included
        participant_ids = {request.user.id} | {p['user_id'] for p in participants_data}
        conversation.participants.set(participant_ids)
        conversation.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Messages.
    Only participants of the conversation can send/view/edit/delete messages.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrParticipant]

    def get_queryset(self):
        # Only messages where the user is a participant of the conversation
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def create(self, request, *args, **kwargs):
        """
        Send a message in an existing conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data.get('conversation').conversation_id
        conversation = get_object_or_404(
            Conversation,
            conversation_id=conversation_id,
            participants=request.user
        )

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_body=serializer.validated_data['message_body']
        )

        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
