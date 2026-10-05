from django.db import models


# Create your models here.
class Excerpt(models.Model):
    philosopher_id = models.TextField()
    author = models.CharField(max_length=100)
    title_of_work = models.CharField(max_length=255)
    quote = models.TextField()
    unique_words = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)

    @property
    def lexical_density(self):
        if not self.total_words:
            return 0

        return self.unique_words // self.total_words
