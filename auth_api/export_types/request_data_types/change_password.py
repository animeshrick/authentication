from typing import Optional

from pydantic import BaseModel


class ChangePasswordRequestType(BaseModel):
    password1: Optional[str] = None
    password2: Optional[str] = None
