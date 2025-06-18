from typing import Optional

from pydantic import BaseModel


class UpdatePasswordRequestType(BaseModel):
    user_id: Optional[str] = None
    password1: Optional[str] = None
    password2: Optional[str] = None
