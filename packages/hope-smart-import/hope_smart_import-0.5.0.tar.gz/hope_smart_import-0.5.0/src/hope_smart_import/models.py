from django.db import models
from hope_flex_fields.models import DataChecker


class Configuration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    checker = models.ForeignKey(DataChecker, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
