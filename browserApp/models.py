from django.db import models

# Create your models here.
class SearchMode(models.Model):
    search_mode = models.TextField(default='academia')