from typing import Optional
from django.db import transaction
from psycopg2 import DatabaseError

from product.export_types.product_types.export_product import ExportProductList, ExportProduct
from product.models.product import Product
from django.core.exceptions import ValidationError

from order.models.order import Order
from cart.models.cart import Cart

class OrderService:
    # @staticmethod
    # def get_all_order_service() -> Optional[ExportProductList]:
    #     try:
    #         subjects = Product.objects.all()
    #     except Exception:
    #         raise DatabaseError()
    #     if subjects:
    #         all_product = ExportProductList(
    #             product_list=[
    #                 ExportProduct(**subject.model_to_dict())
    #                 for subject in subjects
    #             ]
    #         )
    #         return all_product
    #     else:
    #         return None

    @staticmethod
    def create_order_from_cart(cart_id: str, shipping_address: str = None, billing_address: str = None) -> Optional[Order]:
        try:
            with transaction.atomic():
                cart = Cart.objects.select_related('user').prefetch_related('items__product').get(id=cart_id)
                
                if not cart.items.exists():
                    raise ValidationError("Cannot create order from empty cart")
                
                order = Order.objects.create(
                    customer=cart.user,
                    shipping_address=shipping_address,
                    billing_address=billing_address or shipping_address
                )
                
                order.create_from_cart(cart)
                return order
                
        except Cart.DoesNotExist:
            raise ValidationError("Cart not found")
        except Exception as e:
            raise ValidationError(f"Error creating order: {str(e)}")
        
    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Order]:
        try:
            return Order.objects.select_related('customer', 'cart').prefetch_related('order_items__product').get(id=order_id)
        except Order.DoesNotExist:
            return None
            
    @staticmethod
    def get_all_orders(user_id: str = None) -> list[Order]:
        queryset = Order.objects.select_related('customer', 'cart').prefetch_related('order_items__product')
        if user_id:
            queryset = queryset.filter(customer_id=user_id)
        return queryset.order_by('-order_date')