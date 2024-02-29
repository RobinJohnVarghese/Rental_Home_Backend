from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notifications
from .serializers import NotificationsSerializer, UserInterestsSerializer
import json



@receiver(post_save, sender=Notifications)
def notification_post_save_handler(sender, instance, created, **kwargs):
    user = instance.touser
    if user and created:
        channel_layer = get_channel_layer()
        count = Notifications.objects.filter(is_seen=False, touser=user).count()
        serialized_instance = UserInterestsSerializer(instance).data
        async_to_sync(channel_layer.group_send)(
            f"notify_{user.id}",
            {
                "type": "send_notification",
                "value": json.dumps(serialized_instance),
            }
        )