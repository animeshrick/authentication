from typing import List, Optional
from pydantic import BaseModel

class ExportCartItem(BaseModel):
    id: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_price: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    quantity: Optional[str] = None
    stock_left: Optional[str] = None
    is_active: bool
    is_available: bool
    total_price: float
    line_discount: float
    final_price: float

