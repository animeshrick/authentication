from auth_api.models.user_models.user import User
from cart.export_types.export_cart.export_cart import ExportCart
from cart.export_types.request_data_types.add_to_cart import AddToCartRequestType
from cart.models.cart import Cart
from cart.serializers.cart_serializer import CartCreateUpdateSerializer
from cart.services.cart_helper import cart_to_export


class CartServices:

    @staticmethod
    def add_items_to_cart(request_data: AddToCartRequestType) -> ExportCart:
        """
        Add items to user's cart with validation and stock management
        """
        try:
            serializer = CartCreateUpdateSerializer()
            
            # Use the improved stock validation method
            if not serializer.validate_stock_with_transaction(request_data):
                raise ValueError("Stock validation failed")
            
            cart = serializer.create_or_update_cart_item(request_data)
            
            if cart is None:
                raise ValueError("Failed to add items to cart")
            
            return cart_to_export(cart)
            
        except Exception as e:
            raise

    @staticmethod
    def get_user_cart(user_id: str) -> ExportCart:
        """
        Get cart details for a specific user
        """
        try:
            user = User.objects.get(id=user_id, is_deleted=False)
            cart = Cart.objects.get(user=user)
            return cart_to_export(cart)
        except (User.DoesNotExist, Cart.DoesNotExist):
            # Return empty cart using model_to_dict() pattern
            empty_cart_data = {
                "id": None,
                "user": user_id,
                "created_at": None,
                "updated_at": None
            }
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
            user = User.objects.get(id=user_id, is_deleted=False)
            cart = Cart.objects.get(user=user)
            
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
            user = User.objects.get(id=user_id, is_deleted=False)
            cart = Cart.objects.get(user=user)
            
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