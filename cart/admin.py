from django.contrib import admin

from cart.models.cart import Cart
from cart.models.cart_item import CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')  # add created_at if you have timestamp fields
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    list_filter = ('product',)
    search_fields = ('cart__user__username', 'product__name')
