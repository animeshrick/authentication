from auth_api.models.user_models.user import User
from cart.export_types.export_cart.export_cart import ExportCart
from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
from cart.export_types.request_data_types.add_item import AddItemRequestType
from cart.models.cart import Cart
from cart.serializers.cart_serializer import CartCreateUpdateSerializer
from cart.services.cart_helper import cart_to_export
from rest_framework import serializers


class CartServices:

    @staticmethod
    def _get_user_and_cart(user_id):
        """
        Helper to fetch user and cart, creates cart if not found.
        """
        user = User.objects.get(id=user_id, is_deleted=False)
        cart, _ = Cart.objects.get_or_create(user=user)
        return user, cart

    @staticmethod
    def add_items_to_cart(request_data: AddToCartRequestType) -> ExportCart:
        """
        Add items to user's cart with validation and stock management
        If the request is a subset of the current cart, do not update the cart, just return the current cart.
        """
        try:
            user, cart = CartServices._get_user_and_cart(request_data.user_id)
            from cart.models.cart_item import CartItem
            # Get current cart product IDs
            current_cart_items = CartItem.objects.filter(cart=cart)
            current_product_ids = set(str(item.product_id) for item in current_cart_items)
            request_product_ids = set(str(p.product_id) for p in (request_data.products or []))
            # If request is a subset, return current cart using get_user_cart
            if not request_product_ids.issuperset(current_product_ids):
                return CartServices.get_user_cart(str(user.id))
            serializer = CartCreateUpdateSerializer()
            # Use the improved stock validation method
            validation_result = serializer.validate_stock_with_transaction(request_data)
            if validation_result is not True:
                raise serializers.ValidationError(validation_result)
            cart = serializer.create_or_update_cart_item(request_data)
            if cart is None:
                raise serializers.ValidationError("Failed to add items to cart")
            return cart_to_export(cart)
        except Exception as e:
            raise

    @staticmethod
    def get_user_cart(user_id: str) -> ExportCart:
        """
        Get cart details for a specific user
        """
        try:
            user, cart = CartServices._get_user_and_cart(user_id)
            return cart_to_export(cart)
        except (User.DoesNotExist, Cart.DoesNotExist):
            return ExportCart(
                user_id=user_id,
                items=[],
                with_id=False
            )

    @staticmethod
    def remove_item_from_cart(user_id: str, product_id: str) -> ExportCart:
        """
        Remove a specific item from user's cart and restore stock
        """
        try:
            user, cart = CartServices._get_user_and_cart(user_id)
            
            from cart.models.cart_item import CartItem
            from product.models.product import Product
            from django.db import transaction
            
            with transaction.atomic():
                # Use select_for_update to prevent race conditions
                cart_item = CartItem.objects.select_for_update().get(cart=cart, product_id=product_id)
                product = Product.objects.select_for_update().get(id=product_id)
                
                # Restore stock
                restored_quantity = cart_item.quantity
                product.stock += restored_quantity
                product.save()
                
                # Remove cart item
                cart_item.delete()
            
            return cart_to_export(cart)
            
        except (User.DoesNotExist, Cart.DoesNotExist, CartItem.DoesNotExist):
            raise ValueError("Cart or item not found")

    @staticmethod
    def clear_cart(user_id: str) -> ExportCart:
        """
        Clear entire cart and restore all stock
        """
        try:
            user, cart = CartServices._get_user_and_cart(user_id)
            
            from cart.models.cart_item import CartItem
            from django.db import transaction
            
            with transaction.atomic():
                # Use select_for_update to prevent race conditions
                cart_items = CartItem.objects.select_for_update().filter(cart=cart).select_related('product')
                
                # Restore stock for all items
                for cart_item in cart_items:
                    product = cart_item.product
                    restored_quantity = cart_item.quantity
                    product.stock += restored_quantity
                    product.save()
                
                # Clear all cart items
                cart_items.delete()
            
            return cart_to_export(cart)
            
        except (User.DoesNotExist, Cart.DoesNotExist):
            raise ValueError("Cart not found")

    @staticmethod
    def debug_stock_levels(product_id: str) -> dict:
        """
        Debug method to check stock levels for a product
        """
        try:
            from product.models.product import Product
            from cart.models.cart_item import CartItem
            
            product = Product.objects.get(id=product_id)
            cart_items = CartItem.objects.filter(product=product)
            
            total_reserved = sum(item.quantity for item in cart_items)
            
            return {
                "product_name": product.name,
                "current_stock": product.stock,
                "total_reserved_in_carts": total_reserved,
                "available_for_purchase": product.stock + total_reserved,
                "cart_items": [
                    {
                        "user_id": str(item.cart.user.id),
                        "quantity": item.quantity
                    } for item in cart_items
                ]
            }
        except Product.DoesNotExist:
            return {"error": "Product not found"}

    @staticmethod
    def add_single_item_to_cart(request_data: AddItemRequestType) -> ExportCart:
        """
        Add a single item to user's cart with validation and stock management.
        If the item is already in the cart, do not update the cart, just return the current cart.
        """
        try:
            user, cart = CartServices._get_user_and_cart(request_data.user_id)
            from cart.models.cart_item import CartItem
            # Check if the product is already in the cart
            if CartItem.objects.filter(cart=cart, product_id=request_data.product_id).exists():
                return CartServices.get_user_cart(str(user.id))
            # Convert single item request to multi-item format for existing logic
            from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
            from cart.export_types.request_data_types.cart_product import CartProductRequestType
            # Create a single product request
            product_request = CartProductRequestType(
                product_id=request_data.product_id,
                quantity=int(request_data.quantity)
            )
            # Create multi-item request format
            multi_item_request = AddToCartRequestType(
                user_id=request_data.user_id,
                products=[product_request]
            )
            # Use existing logic
            serializer = CartCreateUpdateSerializer()
            # Validate stock
            validation_result = serializer.validate_stock_with_transaction(multi_item_request)
            if validation_result is not True:
                raise serializers.ValidationError(validation_result)
            cart = serializer.create_or_update_cart_item(multi_item_request)
            if cart is None:
                raise serializers.ValidationError("Failed to add item to cart")
            return cart_to_export(cart)
        except Exception as e:
            raise