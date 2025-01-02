from django.db import models


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.city})"
