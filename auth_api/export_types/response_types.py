from typing import Optional, Any, List
from pydantic import BaseModel
from datetime import datetime


class ErrorResponse(BaseModel):
    """
    Generic error response models for all API endpoints
    """
    success: bool = False
    error: str
    details: Optional[List[str]] = None
    timestamp: datetime = datetime.now()
    path: Optional[str] = None
    method: Optional[str] = None


class SuccessResponse(BaseModel):
    """
    Generic success response models for all API endpoints
    """
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: datetime = datetime.now()
    path: Optional[str] = None
    method: Optional[str] = None 