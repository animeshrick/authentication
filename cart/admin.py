from django.contrib import admin

from cart.models.cart import Cart
from cart.models.cart_item import CartItem


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
