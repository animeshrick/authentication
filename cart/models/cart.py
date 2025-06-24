from django.db import models
from auth_api.models.base_models.base_model import GenericBaseModel
from auth_api.models.user_models.user import User

class Cart(GenericBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', db_index=True)

    def __str__(self):
        return f"Cart {self.id} for user {self.user.id}"