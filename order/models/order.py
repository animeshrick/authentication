from django.db import models

from auth_api.models.base_models.base_model import GenericBaseModel
from auth_api.models.user_models.user import User
from order.models.order_payment_status import OrderStatus, PaymentStatus


class Order(GenericBaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=100, unique=True, default=0)

    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    shipping_address = models.TextField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.user.username}"

    def get_total_quantity(self):
        return sum(item.quantity for item in self.order_items.all())

    def get_total_value(self):
        return sum(item.quantity * item.price for item in self.order_items.all())