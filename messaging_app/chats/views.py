from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwnerOrParticipant
from .pagination import StandardResultsSetPagination
from .filters import MessageFilter


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

        participants_data = request.data.get('participants', [])
        participant_ids = {request.user.id} | {p['user_id'] for p in participants_data}

        if not participant_ids:
            return Response(
                {"detail": "You must include at least yourself as a participant."},
                status=status.HTTP_403_FORBIDDEN
            )

        conversation = Conversation.objects.create()
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
    Supports pagination and filtering.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrParticipant]
    pagination_class = StandardResultsSetPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MessageFilter

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

        conversation = serializer.validated_data.get('conversation')
        conversation = get_object_or_404(Conversation, conversation_id=conversation.conversation_id)

        # Explicitly check if user is a participant
        if not conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
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
