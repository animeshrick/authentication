from typing import Optional

from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_validated: bool
    error: Optional[str]
