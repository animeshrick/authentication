from typing import Optional
import uuid
from decimal import Decimal
from pydantic import BaseModel

class ExportCartItem(BaseModel):
    id: Optional[uuid.UUID] = None
    product_id: Optional[uuid.UUID] = None
    product_name: Optional[str] = None
    product_price: Optional[Decimal] = None
    product_sku: Optional[str] = None
    product_slug: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    quantity: int = 1
    stock_left: int = 0
    is_active: bool = True
    is_available: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    product_discount: Optional[Decimal] = None

