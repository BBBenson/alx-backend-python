# messaging/filters.py

import django_filters
from django.utils.translation import gettext_lazy as _

from .models import Message, User


class MessageFilter(django_filters.FilterSet):
    """
    Filter for messages with support for:
    - Filtering by sender ID or username
    - Filtering by date range
    - Search within message content
    """

    sender = django_filters.ModelChoiceFilter(
        field_name="sender",
        queryset=User.objects.all(),
        label=_("Sender (ID or username)"),
        method="filter_sender",
    )

    receiver = django_filters.ModelChoiceFilter(
        field_name="receiver",
        queryset=User.objects.all(),
        label=_("Receiver (ID or username)"),
        method="filter_user",
    )

    start_date = django_filters.DateTimeFilter(
        field_name="timestamp",
        lookup_expr="gte",
        label=_("Sent after (YYYY-MM-DD HH:MM:SS)"),
    )

    end_date = django_filters.DateTimeFilter(
        field_name="timestamp",
        lookup_expr="lte",
        label=_("Sent before (YYYY-MM-DD HH:MM:SS)"),
    )

    search = django_filters.CharFilter(
        field_name="content",
        lookup_expr="icontains",
        label=_("Search in messages"),
    )

    class Meta:
        model = Message
        fields = [
            "sender",
            "receiver",
            "start_date",
            "end_date",
            "search",
            "conversation",
        ]

    def filter_sender(self, queryset, name, value):
        """
        Filter messages by sender ID or username
        """
        if not value:
            return queryset

        try:
            # Try to convert to integer for ID lookup
            sender_id = int(value)
            return queryset.filter(sender__id=sender_id)
        except (ValueError, TypeError):
            # Fall back to username lookup
            return queryset.filter(sender__username__iexact=str(value))

    def filter_user(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(**{f"{name}__pk": value.pk})
