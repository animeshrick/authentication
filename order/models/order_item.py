class OrderItem(GenericBaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.CharField(max_length=100)  # Replace with ForeignKey if needed
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"