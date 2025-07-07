from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from auth_api.models.base_models.base_model import GenericBaseModel
from auth_api.models.user_models.user import User
from cart.models.cart import Cart
from order.models.order_item import OrderItem
from order.models.order_payment_status import OrderStatus, PaymentStatus


class Order(GenericBaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT, related_name='order', null=True)
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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    shipping_address = models.TextField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', 'order_date']),
            models.Index(fields=['order_status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['cart']),
        ]
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.username}"

    def get_total_quantity(self):
        return sum(item.quantity for item in self.order_items.all())

    def get_total_value(self):
        return sum(item.get_subtotal() for item in self.order_items.all())

    def create_from_cart(self, cart):
        self.cart = cart
        self.save()
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=self,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        self.total_amount = self.get_total_value()
        self.save()
        return self

    def can_cancel(self):
        return self.order_status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.RETURNED]

    def can_deliver(self):
        return self.order_status == OrderStatus.SHIPPED

    def mark_as_delivered(self):
        if self.can_deliver():
            self.order_status = OrderStatus.DELIVERED
            self.delivery_date = timezone.now()
            self.save()
            return True
        return False