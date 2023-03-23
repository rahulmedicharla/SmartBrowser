from django.db import models

# Create your models here.
class BrowserContent(models.Model):
    search_mode = models.TextField(default='academia')
    input_question = models.TextField(default="Ask q/a here")
    result = models.TextField(default = "")
    related_link_one = models.TextField(default = "")
    related_link_two = models.TextField(default = "")
    related_link_three = models.TextField(default = "")
    img_link = models.TextField(default="")