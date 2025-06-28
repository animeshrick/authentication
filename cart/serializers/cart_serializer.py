from rest_framework import serializers
from django.contrib.auth import get_user_model
from typing import List, Optional

from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
from cart.export_types.request_data_types.cart_product import CartProductRequestType
from cart.models.cart import Cart
from cart.models.cart_item import CartItem
from cart.services.cart_helper import validate_products_in_stock_all
from product.models.product import Product

User = get_user_model()

class CartCreateUpdateSerializer(serializers.ModelSerializer):

    """
    What cart serializer do
        1. validate all the requested parms
        2. product validations
        3. is product OOS
        4. create or update cart obj
    """

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data: AddToCartRequestType):
        user = User.objects.filter(id=data.user_id, is_deleted=False).first()
        if user is None:
            raise serializers.ValidationError("User not found")
        else:
            request_product_list = data.products
            if request_product_list is None:
                raise serializers.ValidationError("Products list cannot be empty")
            if not validate_products_in_stock_all(request_product_list):
                return False
        return True

    def create_or_update_cart_item(self, request_data: AddToCartRequestType) -> Cart:
        """
        Add or update a cart item. Returns the Cart instance.
        """
        if not self.validate(request_data):
            raise serializers.ValidationError("Validation failed")
        
        # Get or create cart for the user
        user = User.objects.get(id=request_data.user_id)
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Process each product in the request
        products: List[CartProductRequestType] = request_data.products or []
        for product_data in products:
            if product_data.product_id and product_data.quantity:
                product = Product.objects.get(id=product_data.product_id)
                quantity = int(product_data.quantity)
                
                # Get or create cart item
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart, 
                    product=product,
                    defaults={'quantity': quantity}
                )
                
                if not created:
                    # Update existing cart item quantity
                    cart_item.quantity += quantity
                    cart_item.save()
        
        return cart