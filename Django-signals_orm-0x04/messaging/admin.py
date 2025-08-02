# messaging_app/chats/admin.py

"""
Admin registration for chats app models: User, Conversation, Message
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from rest_framework.permissions import IsAdminUser

from .models import Conversation, Message, MessageHistory, Notification

User = get_user_model()


# Custom User Admin configuration
class CustomUserAdmin(UserAdmin):
    """Custom User model display in admin"""

    model = User
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff")
    list_filter = ("is_staff", "is_superuser", "role")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "phone_number", "role")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def has_module_permission(self, request):
        return IsAdminUser().has_permission(request, self)


# Custom Conversation configuration
class ConversationAdmin(admin.ModelAdmin):
    """Admin view for Conversation model"""

    list_display = ("conversation_id", "created_at", "participants_list")
    filter_horizontal = ("participants",)

    def participants_list(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])

    def has_module_permission(self, request):
        return IsAdminUser().has_permission(request, self)


# Custom Message configuration
class MessageAdmin(admin.ModelAdmin):
    """Admin view for Message model"""

    list_display = (
        "message_id",
        "sender",
        "receiver",
        "conversation",
        "timestamp",
        "short_content",
        "parent_message",
    )
    list_filter = ("sender", "receiver", "conversation", "timestamp", "edited")
    search_fields = (
        "content",
        "sender__username",
        "receiver",
    )
    date_hierarchy = "timestamp"

    @admin.display(description="Content")
    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    def has_module_permission(self, request):
        return IsAdminUser().has_permission(request, self)


class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ("message", "edited_by", "edited_at")
    list_filter = ("edited_at", "edited_by")
    search_fields = ("message__content", "edited_by__username")
    readonly_fields = ("message", "content", "edited_by", "edited_at")


# Custom Notification configuration
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message__content")


# Register models with admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(MessageHistory, MessageHistoryAdmin)
