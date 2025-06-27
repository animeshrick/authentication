from typing import List, Optional
import datetime
from pydantic import BaseModel

class ExportCart(BaseModel):
    id: Optional[int]
    user_id: int
    # items: List[ExportCartItem]
    created_at: Optional[datetime.datetime] = None

    def __init__(self, with_id: bool = True, **kwargs):
        if not with_id:
            kwargs["id"] = None
        super().__init__(**kwargs)
