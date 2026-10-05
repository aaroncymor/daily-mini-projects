from django.db import models


# Create your models here.
class Excerpt(models.Model):
    author = models.CharField(max_length=100)
    title_of_work = models.CharField(max_length=255)
    word_count = models.IntegerField(default=0)
    lexical_density = models.DecimalField()
