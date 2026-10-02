from typing import Optional
from django.db import models


# Create your models here.
MEDIA_TYPE_CHOICES = (
    ('anime', 'Anime'),
    ('manga', 'Manga')
)


class BacklogItem(models.Model):

    title = models.TextField()
    mal_id = models.TextField(unique=True)
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE_CHOICES)
    current_progress = models.IntegerField(default=0)
    total_units = models.IntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True)

    @property
    def estimates_in_days(self) -> Optional[int]:
        if not self.start_date or not self.target_date or self.total_units == 0:
            return

        items_left = self.total_units - self.current_progress

        # days_left
        delta = self.target_date - self.start_date
        remaining = delta.days

        print("ITEMS LEFT", items_left)
        print("REMAINING DAYS", remaining)

        return items_left // remaining
