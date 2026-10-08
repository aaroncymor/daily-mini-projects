from django.db import models


# Create your models here.
ANIME_CHOICE = 'anime'
MANGA_CHOICE = 'manga'

CATEGORY_CHOICES = (
    (ANIME_CHOICE, 'Anime'),
    (MANGA_CHOICE, 'Manga'),
)


class Catalog(models.Model):
    title = models.TextField()
    mal_id = models.IntegerField(unique=True)
    url = models.URLField(max_length=255, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    category = models.CharField(max_length=5, choices=CATEGORY_CHOICES)
    catalog_type = models.CharField(max_length=255, blank=True, null=True, default='')
    score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, blank=True, null=True)
    image_url = models.URLField(max_length=255, blank=True, null=True, default='')
    episodes_volumes = models.IntegerField(blank=True, null=True, default=0)
