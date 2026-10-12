from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_by = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_by_user"
    )
    assigned_to = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="assigned_to_user"
    )
