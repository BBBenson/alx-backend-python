# messaging/views.py

"""Viewsets for Conversation and Message models"""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
    method_decorator,
    permission_classes,
)
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import MessageFilter
from .models import Conversation, Message
from .pagination import MessagePagination
from .permissions import IsMessageOwnerOrReadOnly, IsParticipantOfConversation
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    CustomTokenObtainPairSerializer,
    MessageSerializer,
    UserSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that includes user data in the response
    """

    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing user accounts.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "head", "options"]  # Remove delete

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "create":
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter to only show the current user's profile in list view
        Non-staff users can only see their own profile
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Retrieve the current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating conversations
    """

    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    http_method_names = ["get", "post", "head", "options"]  # Disable PUT/PATCH/DELETE
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    search_fields = [
        "participants__first_name",
        "participants__last_name",
        "participants__email",
    ]

    def get_queryset(self):
        # Get conversations where current user is a participant
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related("participants", "messages")

    def get_serializer_class(self) -> type:
        if self.action == "list":
            return ConversationListSerializer
        return ConversationDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add current user to participants if not included
        participants = serializer.validated_data.get("participants", [])
        if request.user not in participants:
            participants.append(request.user)

        conversation = serializer.save(participants=participants)
        return Response(
            ConversationDetailSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
        )

    def get_object(self):
        """
        Override to ensure proper permission checking for object retrieval
        """
        obj = super().get_object()
        if not obj.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied(
                "You do not have permission to access this conversation",
                code=status.HTTP_403_FORBIDDEN,
            )
        return obj


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating messages within a conversation
    """

    serializer_class = MessageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsParticipantOfConversation,
        IsMessageOwnerOrReadOnly,
    ]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = MessageFilter
    pagination_class = MessagePagination
    ordering_fields = ["timestamp"]
    search_fields = ["content"]

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        """
        List all messages in a conversation with caching.
        Cache timeout is set to 60 seconds.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        # Get conversation ID from URL
        conversation_id = self.kwargs.get("conversation_id")

        # Verify conversation exists and user is participant
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found")

        if not conversation.participants.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied(
                "You are not a participant in this conversation",
                code=status.HTTP_403_FORBIDDEN,
            )

        # Get the base queryset with optimized field selection
        queryset = (
            Message.objects.filter(
                conversation_id=conversation_id,
                parent_message__isnull=True,  # Only get top-level messages by default
            )
            .select_related("sender", "receiver", "conversation")
            .prefetch_related("replies__sender", "replies__receiver")
            .only(
                "message_id",
                "sender__id",
                "sender__username",
                "receiver__id",
                "receiver__username",
                "conversation__id",
                "content",
                "timestamp",
                "edited",
                "is_thread",
                "parent_message_id",
                "read",
            )
            .order_by("-timestamp")
        )

        # Apply any filters
        queryset = self.filter_queryset(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        # Get conversation ID from URL
        conversation_id = self.kwargs.get("conversation_id")

        # Verify conversation exists and user is participant
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found")

        if not conversation.participants.filter(id=request.user.id).exists():
            raise PermissionDenied(
                "You are not a participant in this conversation",
                code=status.HTTP_403_FORBIDDEN,
            )

        # Create message with current user as sender
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user, conversation=conversation)

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Check if user is the message owner
        if instance.sender != request.user:
            raise PermissionDenied(
                "You can only edit your own messages", code=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if user is the message owner
        if instance.sender != request.user:
            raise PermissionDenied(
                "You can only delete your own messages", code=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def thread(self, request, conversation_id=None, pk=None):
        """Get a message and all its replies as a thread"""
        message = self.get_object()
        thread_messages = message.get_thread(include_self=True)
        serializer = self.get_serializer(thread_messages, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        conversation_id = self.kwargs.get("conversation_id")
        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Check if user is a participant in the conversation
        if not conversation.participants.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied("You are not a participant in this conversation")

        parent_message_id = serializer.validated_data.get("parent_message")
        if parent_message_id:
            parent_message = get_object_or_404(Message, id=parent_message_id)
            if parent_message.conversation.conversation_id != conversation_id:
                raise ValidationError("Parent message must be in the same conversation")

            serializer.save(
                sender=self.request.user,
                conversation=conversation,
                parent_message=parent_message,
            )
        else:
            serializer.save(sender=self.request.user, conversation=conversation)


class UnreadMessagesView(APIView):
    """
    View for retrieving and managing unread messages.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve all unread messages for the current user.
        Uses the custom unread manager with optimized queries.
        """
        # Use the custom manager to get unread messages
        unread_messages = Message.unread.unread_for_user(request.user)

        # Paginate the results
        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """
        Mark specified messages as read.
        Expects a list of message IDs in the request data.
        """
        message_ids = request.data.get("message_ids", [])
        if not isinstance(message_ids, list):
            return Response(
                {"error": "message_ids must be a list of message IDs"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use the custom manager to mark messages as read
        updated_count = Message.unread.mark_as_read(message_ids, request.user)

        return Response(
            {"status": f"Marked {updated_count} message(s) as read"},
            status=status.HTTP_200_OK,
        )

    def get_paginator(self):
        if not hasattr(self, "_paginator"):
            self._paginator = PageNumberPagination()
            self._paginator.page_size = 20
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.get_paginator().paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.get_paginator().get_paginated_response(data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    Delete the currently authenticated user and all their associated data.
    """
    try:
        user = request.user
        # The actual deletion will trigger the post_delete signal
        user.delete()
        return Response(
            {"detail": "User account and all associated data have been deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
