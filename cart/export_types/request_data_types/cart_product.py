from typing import Optional
from pydantic import BaseModel

class CartProductRequestType(BaseModel):
    product_id: Optional[str] = None
    quantity: Optional[int ] = None