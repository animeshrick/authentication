from typing import Optional
import uuid
from pydantic import BaseModel

class CartProductRequestType(BaseModel):
    product_id: Optional[uuid.UUID] = None
    quantity: Optional[int] = None