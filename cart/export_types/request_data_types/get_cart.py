from typing import Optional
import uuid
from pydantic import BaseModel, Field


class GetCartRequestType(BaseModel):
    user_id: uuid.UUID = Field(..., description="User ID to get cart for") 