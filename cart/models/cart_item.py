from django.db import models
from auth_api.models.base_models.base_model import GenericBaseModel
from cart.models.cart import Cart
from product.models.product import Product

class CartItem(GenericBaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Quantity added

    class Meta:
        unique_together = ('cart', 'product')  # Prevent same product multiple times in one cart

    def __str__(self):
        return f"{self.product.stock} x {self.product.name} in cart {self.cart.id}"