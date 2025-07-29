from django.db import models


class Household(models.Model):
    name = models.CharField(max_length=100)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Individual(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.household.name} - {self.pk}"
