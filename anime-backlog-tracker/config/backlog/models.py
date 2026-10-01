from django.db import models


# Create your models here.
MEDIA_TYPE_CHOICES = (
    ('anime', 'Anime'),
    ('manga', 'Manga')
)


class BacklogItem(models.Model):

    title = models.CharField(max_length=255)
    mal_id = models.TextField()
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES)
    current_progress = models.IntegerField(default=0)
    total_units = models.IntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)
