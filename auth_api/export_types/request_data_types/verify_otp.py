from typing import Optional

from pydantic import BaseModel


class VerifyOTPRequestType(BaseModel):
    email: Optional[str] = None
    otp: Optional[str] = None
