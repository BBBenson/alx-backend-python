from rest_framework import viewsets, status
from rest_framework.response import Response
from django_filters import rest_framework as filters

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


# Conversation filters if needed
class ConversationFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Conversation
        fields = ['created_at']


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ConversationFilter

    def create(self, request, *args, **kwargs):
        """
        Override create to handle creating conversation with participants
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = Conversation.objects.create()
        participants_data = request.data.get('participants', [])
        conversation.participants.set([p['user_id'] for p in participants_data])
        conversation.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create to send a message in an existing conversation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation_id = request.data.get('conversation')
        conversation = Conversation.objects.get(conversation_id=conversation_id)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            message_body=serializer.validated_data['message_body']
        )
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )
