from django.db import models
from django.utils.text import slugify
import uuid
from django.core.exceptions import ValidationError

from auth_api.models.base_models.base_model import GenericBaseModel
from product.models.category import Category


class Product(GenericBaseModel):
    """
    Product models for e-commerce use cases:
    - Add to cart
    - Search
    - Show Product Detail Page (PDP)
    - Show Out Of Stock (OOS)
    - Associate with individual orders
    """
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=32, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, help_text="Number of items in stock")
    image = models.URLField(max_length=1024, blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount percentage (e.g., 10 for 10%)", blank=True, null=True)

    @property
    def is_out_of_stock(self):
        return self.stock == 0

    def save(self, *args, **kwargs):
        if self.stock <= 0:
            raise ValidationError("Product stock must be greater than 0 to add the product.")
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if not self.sku:
            # Generate a unique SKU
            sku = uuid.uuid4().hex[:12].upper()
            while Product.objects.filter(sku=sku).exclude(pk=self.pk).exists():
                sku = uuid.uuid4().hex[:12].upper()
            self.sku = sku
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["category"]),
            models.Index(fields=["discount"]),
        ] 