from rest_framework import serializers
from typing import List, Optional
from django.core.exceptions import ObjectDoesNotExist

from auth_api.models.user_models.user import User
from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
from cart.export_types.request_data_types.cart_product import CartProductRequestType
from cart.models.cart import Cart
from cart.models.cart_item import CartItem
from cart.services.cart_helper import validate_products_in_stock_all
from product.models.product import Product


class CartCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Cart serializer for creating and updating cart items
    Handles validation, stock management, and cart operations
    """

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data: AddToCartRequestType):
        # Validate user exists and is active
        try:
            user = User.objects.get(id=data.user_id, is_deleted=False)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid user_id: User not found or inactive")
        
        # Validate products list
        if data.products is None:
            raise serializers.ValidationError("Products list cannot be empty")
        
        # Validate each product
        for product_data in data.products:
            if not product_data.product_id:
                raise serializers.ValidationError("Product ID is required")
            
            if not product_data.quantity or product_data.quantity <= 0:
                raise serializers.ValidationError(f"Invalid quantity for product {product_data.product_id}: Quantity must be greater than 0")
            
            # Check if product exists and is active
            try:
                product = Product.objects.get(id=product_data.product_id)
                if not product.is_active:
                    raise serializers.ValidationError(f"Product '{product.name}' is inactive")
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"Invalid product_id: Product with ID {product_data.product_id} not found")
        
        # Validate stock availability
        if not validate_products_in_stock_all(data.products, str(data.user_id)):
            return False
        return True

    def create_or_update_cart_item(self, request_data: AddToCartRequestType) -> Cart | None:
        """
        Add or update cart items with optimized database operations
        """
        if self.validate(request_data):
            user = User.objects.get(id=request_data.user_id)
            cart, cart_created = Cart.objects.get_or_create(user=user)

            requested_products: List[CartProductRequestType] = request_data.products or []
            product_ids = [p.product_id for p in requested_products]
            
            # Bulk fetch products and cart items
            products = Product.objects.filter(id__in=product_ids)
            product_map = {p.id: p for p in products}
            cart_items = CartItem.objects.filter(cart=cart, product_id__in=product_ids)
            cart_item_map = {item.product_id: item for item in cart_items}

            # Prepare bulk operations
            products_to_update = []
            cart_items_to_update = []
            cart_items_to_create = []

            for product_data in requested_products:
                product = product_map.get(product_data.product_id)
                quantity = int(product_data.quantity)
                
                if not product:
                    continue
                    
                cart_item = cart_item_map.get(product.id)
                
                if cart_item:
                    # Update existing cart item
                    old_quantity = cart_item.quantity
                    new_quantity = quantity
                    stock_adjustment = new_quantity - old_quantity
                    
                    if stock_adjustment != 0:
                        product.stock -= stock_adjustment
                        products_to_update.append(product)
                    
                    cart_item.quantity = new_quantity
                    cart_items_to_update.append(cart_item)
                else:
                    # Create new cart item
                    cart_item = CartItem(cart=cart, product=product, quantity=quantity)
                    cart_items_to_create.append(cart_item)
                    product.stock -= quantity
                    products_to_update.append(product)

            # Execute bulk operations
            if products_to_update:
                Product.objects.bulk_update(products_to_update, ["stock"])
            if cart_items_to_update:
                CartItem.objects.bulk_update(cart_items_to_update, ["quantity"])
            if cart_items_to_create:
                CartItem.objects.bulk_create(cart_items_to_create)

            return cart
        return None