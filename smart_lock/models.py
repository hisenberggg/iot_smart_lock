from django.db import models


# Create your models here.
class logs(models.Model):
    NAME = models.CharField(max_length=30)
    VISIT_TIME = models.DateTimeField(auto_now_add=True)
