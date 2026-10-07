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
    url = models.URLField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=5, choices=CATEGORY_CHOICES)
    catalog_type = models.CharField()
    score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    image_url = models.URLField(max_length=255)
    episodes_volumes = models.IntegerField()
