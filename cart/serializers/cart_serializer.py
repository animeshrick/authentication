# cart/serializers/cart_item_create.py

from rest_framework import serializers

from cart.models.cart_item import CartItem
from product.models.product import Product

class CartItemCreateUpdateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data: CartItem):
        product = Product.objects.filter(id=data.pr).first()
        if not product:
            raise serializers.ValidationError(f"Product ID {data['product_id']} not found.")
        if not product.is_active:
            raise serializers.ValidationError(f"Product '{product.name}' is not active.")
        if product.stock < data["quantity"]:
            raise serializers.ValidationError(f"Insufficient stock for product '{product.name}'.")
        return data

    def create_or_update_cart_item(self, cart: CartItem):
        """
        Add or update a cart item. Returns the CartItem instance.
        """
        validated_data = self.validated_data
        product = Product.objects.get(id=validated_data["product_id"])
        quantity = validated_data["quantity"]

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity if not created else quantity
        cart_item.save()
        return cart_item