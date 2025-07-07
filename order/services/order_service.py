from typing import Optional
from uuid import UUID

from psycopg2 import DatabaseError

from product.export_types.product_types.export_product import ExportProductList, ExportProduct
from product.models.product import Product
from product.models.category import Category

class OrderService:
    @staticmethod
    def get_all_order_service() -> Optional[ExportProductList]:
        # try:
        #     subjects = Product.objects.all()
        # except Exception:
        #     raise DatabaseError()
        # if subjects:
        #     all_product = ExportProductList(
        #         product_list=[
        #             ExportProduct(**subject.model_to_dict())
        #             for subject in subjects
        #         ]
        #     )
        #     return all_product
        # else:
        #     return None
        return []

    # @staticmethod
    # def get_subject_service(product_id: str) -> Optional[ExportProduct]:
    #     try:
    #         subject = Product.objects.get(id=product_id)
    #     except Exception:
    #         raise ValueError("This product is not listed.")
    #     if subject:
    #         return ExportProduct(**subject.model_to_dict())
    #     else:
    #         return None