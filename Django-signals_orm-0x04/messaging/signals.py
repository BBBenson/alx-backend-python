# messaging/signals.py

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Message, MessageHistory, Notification


@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a notification when a new message is sent.
    """
    if created:  # Only create notification for new messages
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content has changed
                MessageHistory.objects.create(
                    message=instance,
                    content=old_message.content,
                    edited_by=instance.sender,
                )
        except Message.DoesNotExist:
            pass  # New message, no history to log


User = get_user_model()


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Clean up user-related data when a user is deleted.
    This includes:
    - Messages sent by the user
    - Messages received by the user
    - Notifications related to the user
    - Message history entries where the user was the editor
    """
    try:
        # Delete messages where user is sender or receiver
        Message.objects.filter(sender=instance).delete()
        Message.objects.filter(receiver=instance).delete()

        # Delete notifications related to the user
        Notification.objects.filter(user=instance).delete()

        # Delete message history where user was the editor
        MessageHistory.objects.filter(edited_by=instance).delete()

    except Exception as e:
        # Log the error
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error cleaning up user data for user {instance.id}: {str(e)}")


@receiver(post_save, sender=Message)
def update_thread_metadata(sender, instance, created, **kwargs):
    """
    Update thread metadata when a new reply is added
    """
    if created and instance.parent_message:
        # Update the parent message's is_thread flag
        if not instance.parent_message.is_thread:
            instance.parent_message.is_thread = True
            instance.parent_message.save(update_fields=["is_thread"])
