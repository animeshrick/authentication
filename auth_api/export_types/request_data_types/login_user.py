from typing import Optional

from pydantic import BaseModel


class LoginRequestType(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
