from django.contrib import admin
from order.models.order import Order
from order.models.order_item import OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'get_subtotal')
    fields = ('product', 'product_name', 'quantity', 'price', 'get_subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'order_status', 'payment_status', 
                   'total_amount', 'order_date', 'delivery_date')
    list_filter = ('order_status', 'payment_status', 'order_date', 'delivery_date')
    search_fields = ('order_number', 'customer__username', 'shipping_address', 'billing_address')
    readonly_fields = ('order_number', 'total_amount', 'order_date', 'delivery_date', 'get_total_quantity', 'get_total_value')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'cart')
        }),
        ('Status', {
            'fields': ('order_status', 'payment_status')
        }),
        ('Financial', {
            'fields': ('total_amount', 'get_total_quantity', 'get_total_value')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Dates', {
            'fields': ('order_date', 'delivery_date')
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('customer', 'cart')
        return self.readonly_fields

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'product_name', 'quantity', 'price', 'get_subtotal')
    list_filter = ('order__order_status', 'order__payment_status')
    search_fields = ('order__order_number', 'product_name', 'product__name')
    readonly_fields = ('get_subtotal',)
    raw_id_fields = ('order', 'product')
