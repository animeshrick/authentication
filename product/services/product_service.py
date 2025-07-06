from typing import Optional
from uuid import UUID

from psycopg2 import DatabaseError

from product.export_types.product_types.export_product import ExportProductList, ExportProduct
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

    @staticmethod
    def get_all_product_service() -> Optional[ExportProductList]:
        try:
            subjects = Product.objects.all()
        except Exception:
            raise DatabaseError()
        if subjects:
            all_product = ExportProductList(
                subject_list=[
                    ExportProduct(**subject.model_to_dict())
                    for subject in subjects
                ]
            )
            return all_product
        else:
            return None

    @staticmethod
    def get_subject_service(product_id: str) -> Optional[ExportProduct]:
        try:
            subject = Product.objects.get(id=product_id)
        except Exception:
            raise ValueError("This product is not listed.")
        if subject:
            return ExportProduct(**subject.model_to_dict())
        else:
            return None