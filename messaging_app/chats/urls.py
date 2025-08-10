# messaging_app/chats/urls.py

"""
URL configuration for chats app
"""

from django.urls import include, path
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    ConversationViewSet,
    CustomTokenObtainPairView,
    MessageViewSet,
    UserViewSet,
)

# Create a router and register viewsets
router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"conversations", ConversationViewSet, basename="conversation")

# Create nested router for messages within conversations
conversations_router = NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)
conversations_router.register(
    r"messages", MessageViewSet, basename="conversation-messages"
)

app_name = "chats"

# Custom URL patterns for nested routes
urlpatterns = [
    # Main router URLs (includes conversations CRUD)
    path("", include(router.urls)),
    # JWT Authentication URLs
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Nested router URLs (includes messages within conversations)
    path("", include(conversations_router.urls)),
    # Alternative explicit routes if nested router isn't available
    path(
        "conversations/<uuid:conversation_id>/messages/",
        MessageViewSet.as_view({"get": "list", "post": "create"}),
        name="conversation-messages-list",
    ),
    path(
        "conversations/<uuid:conversation_id>/messages/<uuid:pk>/",
        MessageViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="conversation-messages-detail",
    ),
]
