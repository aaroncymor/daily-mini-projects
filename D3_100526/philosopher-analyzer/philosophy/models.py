from django.db import models


# Create your models here.
class Philosopher(models.Model):
    philosopher_id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)


class Excerpt(models.Model):
    quote_id = models.UUIDField(primary_key=True)
    quote = models.TextField()
    philosopher = models.ForeignKey(
        Philosopher,
        on_delete=models.CASCADE,
        related_name='excerpts'
    )
    title_of_work = models.CharField(max_length=255)
    unique_words = models.IntegerField(default=0)
    total_words = models.IntegerField(default=0)

    @property
    def lexical_density(self):
        if not self.total_words:
            return 0

        return self.unique_words // self.total_words
