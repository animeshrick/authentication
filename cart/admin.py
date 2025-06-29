from django.contrib import admin

from cart.models.cart import Cart
from cart.models.cart_item import CartItem
from cart.models.order_summary import OrderSummary


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')  # add created_at if you have timestamp fields
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'product', 'quantity', 'cart_id')
    list_filter = ('product',)
    search_fields = ('cart__user__username', 'product__name')
    
    def user_name(self, obj):
        return obj.cart.user.username if obj.cart and obj.cart.user else 'N/A'
    user_name.short_description = 'User Name'
    
    def cart_id(self, obj):
        return obj.cart.id if obj.cart else 'N/A'
    cart_id.short_description = 'Cart ID'

@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cart_amount', 'cart_item_discount', 'shipping_charge', 'round_of_val',
        'can_cod', 'total_items', 'total_quantity', 'payment_method', 'currency', 'created_at', 'updated_at'
    )
    search_fields = ('id', 'can_cod', 'payment_method', 'currency')
    list_filter = ('currency', 'can_cod')
