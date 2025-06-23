from django.contrib import admin
from product.models.product import Product
from product.models.category import Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sku", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active", "brand")
    search_fields = ("name", "sku", "slug", "brand")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("sku",)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
