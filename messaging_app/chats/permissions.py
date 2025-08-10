# messaging_app/chats/permissions.py

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the conversation/message.
        if hasattr(obj, "sender") and obj.sender == request.user:
            return True
        if hasattr(obj, "participants") and request.user in obj.participants.all():
            return True
        return False


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """

    message = "You must be a participant of this conversation."

    def has_permission(self, request, view):
        # Allow GET, OPTIONS, or HEAD requests for listing conversations
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # For other methods (POST, PUT, PATCH, DELETE), require authentication
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read permissions to any authenticated user who is a participant
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.participants.all()

        # For write permissions (PUT, PATCH, DELETE), check if the user is a participant
        # and the request is for a message (not a conversation)
        if hasattr(obj, "conversation"):  # This is a Message object
            return request.user in obj.conversation.participants.all()

        # For conversation objects, check if user is a participant
        return request.user in obj.participants.all()


class IsMessageOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a message to edit or delete it.
    """

    message = "You must be the owner of this message to perform this action."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()

        # Write permissions are only allowed to the owner of the message.
        return obj.sender == request.user
