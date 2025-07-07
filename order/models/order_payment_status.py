from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"
    RETURNED = "returned", "Returned"


class PaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Unpaid"
    PAID = "paid", "Paid"
    REFUNDED = "refunded", "Refunded"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    FAILED = "failed", "Failed"
