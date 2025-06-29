from pydantic import BaseModel
from typing import Optional
import uuid

class AddItemRequestType(BaseModel):
    user_id: uuid.UUID
    product_id: uuid.UUID
    quantity: str 