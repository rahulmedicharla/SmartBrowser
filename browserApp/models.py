from django.db import models

# Create your models here.
class Temp(models.Model):
    text_input = models.CharField(max_length=100)
