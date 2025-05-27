from django.db import models


class AccountType(models.TextChoices):
    REGULAR = "regular", "Regular"
    SILVER = "silver", "Silver"
    GOLD = "gold", "Gold"
    PLATINUM = "platinum", "Platinum"
