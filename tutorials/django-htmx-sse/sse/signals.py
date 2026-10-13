from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Task
from .consumers import SerializedTask


@receiver(post_save, sender=Task)
def task_event_handler(sender, instance, created, **kwargs):
    if instance.assigned_to is None:
        return
    channel_layer = get_channel_layer()
    username = instance.assigned_to.username
    task = SerializedTask.to_dict(instance)
    print(f"[signal] sending to group sse_{username}") 
    async_to_sync(channel_layer.group_send)(
        f"sse_{username}",
        {"type": "sse.event", "task": task},
    )


@receiver(pre_delete, sender=Task)
def task_deletion_handler(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    username = instance.assigned_to.username
    task = SerializedTask.to_dict(instance)

    async_to_sync(channel_layer.group_send)(
        f"sse_{username}",
        {"type": "sse.event", "task": task}
    )
