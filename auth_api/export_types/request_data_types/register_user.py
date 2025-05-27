from typing import Optional

from pydantic import BaseModel


class RegisterUserRequestType(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    account_type: Optional[str] = None
