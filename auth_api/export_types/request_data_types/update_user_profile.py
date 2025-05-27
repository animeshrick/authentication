from typing import Optional

from pydantic import BaseModel


class UpdateUserProfileRequestType(BaseModel):
    fname: Optional[str] = None
    lname: Optional[str] = None
    dob: Optional[str] = None
    phone: Optional[str] = None
    image: Optional[str] = None
