from django.db import models

from auth_api.models.base_models.base_model import GenericBaseModel
from auth_api.models.deifinitions import AccountType


class AbstractUser(GenericBaseModel):
    username = models.CharField(max_length=25, null=False, unique=True)
    email = models.EmailField(
        verbose_name="Email", max_length=255, unique=True, null=False
    )
    account_type = models.CharField(
        max_length=10, choices=AccountType.choices, default=AccountType.REGULAR
    )
    name = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=False)
    address = models.CharField(max_length=500, null=True)
    pincode = models.CharField(max_length=6, null=True, default="713216")
    lat = models.CharField(max_length=20, null=True)
    lan = models.CharField(max_length=20, null=True)
    dob = models.DateField(null=True)
    phone = models.CharField(max_length=10, null=True)
    image = models.CharField(max_length=2555, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]

    def __str__(self):
        return self.email

    @property
    def get_phone(self):
        """Fetch registered Phone Number of the user"""
        if self.phone:
            return self.phone

    @property
    def get_is_active(self):
        return self.is_active

    @property
    def get_username(self):
        if self.username:
            return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
