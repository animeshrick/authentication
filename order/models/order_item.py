from django.db import models
from django.core.validators import MinValueValidator

from auth_api.models.base_models.base_model import GenericBaseModel
from product.models.product import Product

class OrderItem(GenericBaseModel):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
            models.Index(fields=['product_name']),
        ]
        unique_together = ('order', 'product')  # Prevent duplicate products in an order

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def get_subtotal(self):
        if self.quantity is None or self.price is None:
            return 0
        return self.quantity * self.price