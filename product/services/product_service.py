from product.models.product import Product
from product.models.category import Category

class ProductService:
    @staticmethod
    def is_unique_sku(sku: str) -> bool:
        """
        Check if the given SKU is unique among all products.
        Returns True if unique, False otherwise.
        """
        return not Product.objects.filter(sku=sku).exists()

    @staticmethod
    def is_unique_product_name_in_category(name: str, category: Category) -> bool:
        """
        Check if the given product name is unique within the specified category.
        Returns True if unique, False otherwise.
        """
        return not Product.objects.filter(name=name, category=category).exists() 