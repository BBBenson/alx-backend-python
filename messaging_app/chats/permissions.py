from typing import Any
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

class IsOwnerOrParticipant(permissions.BasePermission):
    def has_object_permission(
        self, request: Request, view: APIView, obj: Any
    ) -> bool:
        if hasattr(obj, 'sender') and hasattr(obj, 'recipient'):
            return obj.sender == request.user or obj.recipient == request.user
        if hasattr(obj, 'participants'):
            return obj.participants.filter(id=request.user.id).exists()
        return False
