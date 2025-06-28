from typing import Optional
import uuid
from pydantic import BaseModel, Field


class RemoveFromCartRequestType(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID")
    product_id: uuid.UUID = Field(..., description="Product ID to remove from cart") 