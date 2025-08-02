# messaging/managers.py

from django.db import models


class UnreadMessagesManager(models.Manager):
    """Custom manager for Message model to handle unread messages."""

    def unread_for_user(self, user):
        """
        Returns a queryset of unread messages for the specified user.
        Uses .only() to fetch only necessary fields for better performance.
        """
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .select_related("sender", "conversation")
            .only(
                "message_id",
                "sender__id",
                "sender__username",
                "content",
                "timestamp",
                "conversation__id",
                "read",
            )
        )

    def mark_as_read(self, message_ids, user):
        """
        Mark specified messages as read for the given user.
        Returns the number of messages marked as read.
        """
        return self.filter(
            message_id__in=message_ids, receiver=user, read=False
        ).update(read=True)
