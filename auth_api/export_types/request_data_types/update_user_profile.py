from typing import Optional

from pydantic import BaseModel


class UpdateUserProfileRequestType(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[str] = None
