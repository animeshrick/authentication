import datetime
from typing import List
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExportUser(BaseModel):
    id: Optional[UUID]
    email: str
    username: Optional[str] = None
    account_type: Optional[str] = None
    dob: Optional[datetime.datetime] = None
    phone: Optional[str] = None
    image: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    lat: Optional[str] = None
    lan: Optional[str] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    def __init__(self, with_id: bool = True, **kwargs):
        if not with_id:
            kwargs["id"] = None
        super().__init__(**kwargs)


class ExportUserList(BaseModel):
    user_list: List[ExportUser]
