from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cover = models.CharField(
        max_length=10,
        choices=CoverChoices.choices
    )

