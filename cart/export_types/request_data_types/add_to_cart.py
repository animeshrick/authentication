from typing import List, Optional
import uuid
from pydantic import BaseModel

from cart.export_types.request_data_types.cart_product import CartProductRequestType


class AddToCartRequestType(BaseModel):
    user_id: Optional[uuid.UUID] = None
    products: Optional[List[CartProductRequestType]] = None
