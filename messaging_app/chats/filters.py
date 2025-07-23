import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    created_at = django_filters.DateTimeFromToRangeFilter()
    sender = django_filters.NumberFilter(field_name='sender__id')
    recipient = django_filters.NumberFilter(field_name='recipient__id')

    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'created_at']
