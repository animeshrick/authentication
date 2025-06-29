from django.db import models

from auth_api.models.base_models.base_model import GenericBaseModel

class OrderSummary(GenericBaseModel):
    cart_amount = models.DecimalField(max_digits=12, decimal_places=2)
    cart_item_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    shipping_charge = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    round_of_val = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    can_cod = models.CharField(max_length=3, null=True, blank=True)
    total_items = models.IntegerField(null=True, blank=True)
    total_quantity = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    currency = models.CharField(max_length=10, default='INR', null=True, blank=True)

    class Meta:
        verbose_name = 'Order Summary'
        verbose_name_plural = 'Order Summaries'
        indexes = [
            models.Index(fields=["cart_amount"]),
            models.Index(fields=["cart_item_discount"]),
        ]

    def __str__(self):
        return f"OrderSummary: {self.id} - {self.cart_amount} {self.currency}" 