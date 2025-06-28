from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        app_label = 'category'  # Explicitly set the app_label

    def __str__(self):
        return self.name

