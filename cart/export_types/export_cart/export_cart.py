from typing import List, Optional
import datetime
import uuid
from pydantic import BaseModel
from cart.export_types.export_cart.export_cart_item import ExportCartItem

class ExportCart(BaseModel):
    id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    items: List[ExportCartItem] = []
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    def __init__(self, with_id: bool = True, **kwargs):
        if not with_id:
            kwargs["id"] = None
        super().__init__(**kwargs)
