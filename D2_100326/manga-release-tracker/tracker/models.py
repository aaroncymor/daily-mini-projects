from django.db import models


# Create your models here.
class MangaSubscription(models.Model):
    manga_id = models.UUIDField(unique=True)
    title = models.TextField()
    status = models.CharField(max_length=50)
    is_subscribed = models.BooleanField(default=False)
    current_chapter = models.CharField(null=True, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)


class NotificationLog(models.Model):
    subject = models.TextField()
    message_body = models.TextField()
    sent_at = models.DateTimeField()

