from typing import List, Optional
from pydantic import BaseModel

from cart.export_types.request_data_types.cart_product import CartProductRequestType


class AddToCartRequestType(BaseModel):
    user_id: Optional[str] = None
    products: Optional[List[CartProductRequestType]] = None
