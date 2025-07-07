from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from _decimal import Decimal

from product.export_types.product_types.export_category import ExportCategory


class ExportOrder(BaseModel):
    id: Optional[UUID]
    name: Optional[str] = None
    slug: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    image: Optional[str] = None
    category: ExportCategory
    brand: Optional[str] = None
    discount: Optional[Decimal] = None
    is_active: bool

    def __init__(self, **kwargs):
        # if kwargs.get("category"):
        #     kwargs["category"] = ExportCategory(
        #         **kwargs["category"].model_to_dict()
        #     )
        super().__init__(**kwargs)


class ExportOrderList(BaseModel):
    product_list: List[ExportOrder]