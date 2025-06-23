from django.db import models
from django.conf import settings
from auth_api.models.base_models.base_model import GenericBaseModel

class Cart(GenericBaseModel):
    user_id = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    guest_id = models.CharField(max_length=50, null=True, blank=True)
    arrange = models.CharField(max_length=20, default="none")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user_id:
            return f"Cart for User {self.user_id}" 
        return f"Guest Cart {self.guest_id}"

    @classmethod
    def create_from_request(cls, retail_params):
        """
        Create a cart from the RetailParams request structure
        """
        cart = cls.objects.create(
            user_id=retail_params.get('UserId'),
            created_by=retail_params.get('CreatedBy'),
            guest_id=retail_params.get('GuestId'),
            arrange=retail_params.get('arrange', 'none')
        )
        return cart 