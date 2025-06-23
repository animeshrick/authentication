from django.db import models
from auth_api.models.base_models.base_model import GenericBaseModel
from cart.models.cart import Cart
from product.models.product import Product

class CartItem(GenericBaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_count = models.PositiveIntegerField(default=1)
    ref_order_id = models.CharField(max_length=50, blank=True, null=True)
    promo_sale_id = models.CharField(max_length=50, blank=True, null=True)
    promo_sale_disc_pct = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_count} x {self.product.name} in cart {self.cart.id}"

    @classmethod
    def create_from_request(cls, cart, product_data):
        """
        Create a cart item from the Products array structure
        """
        try:
            product = Product.objects.get(id=product_data.get('ProductId'))
        except Product.DoesNotExist:
            raise ValueError(f"Product with ID {product_data.get('ProductId')} does not exist")
        
        cart_item = cls.objects.create(
            cart=cart,
            product=product,
            product_count=product_data.get('ProductCount', 1),
            ref_order_id=product_data.get('RefOrderID', ''),
            promo_sale_id=product_data.get('PromoSaleId', ''),
            promo_sale_disc_pct=product_data.get('PromoSaleDiscPct', '')
        )
        return cart_item 