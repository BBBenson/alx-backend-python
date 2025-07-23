from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation/message
    to view, send, update or delete.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        # Only allow authenticated users at all
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        # Check if user is part of the conversation/message
        if hasattr(obj, 'sender') and hasattr(obj, 'recipient'):
            is_participant = obj.sender == request.user or obj.recipient == request.user
        elif hasattr(obj, 'participants'):
            is_participant = obj.participants.filter(id=request.user.id).exists()
        else:
            return False

        # Optionally: only allow modifications for certain methods
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return is_participant  # Only participants can modify/delete

        # For GET/POST also allow if participant
        return is_participant
