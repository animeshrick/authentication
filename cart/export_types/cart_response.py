from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from auth_api.export_types.response_types import SuccessResponse
from cart.export_types.export_cart.export_cart import ExportCart


class CartSuccessResponse(SuccessResponse):
    """
    Cart-specific success response model
    """
    data: Optional[ExportCart] = None
    cart_id: Optional[str] = None
    total_items: Optional[int] = None
    total_value: Optional[float] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-calculate cart metrics if data is provided
        if self.data and hasattr(self.data, 'items'):
            self.cart_id = str(self.data.id) if self.data.id else None
            self.total_items = len(self.data.items) if self.data.items else 0
            self.total_value = sum(
                float(item.final_price) if item.final_price else 0 
                for item in self.data.items
            ) if self.data.items else 0.0 