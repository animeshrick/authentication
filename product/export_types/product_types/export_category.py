import typing
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExportCategory(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    slug: Optional[str] = None


class ExportCategoryList(BaseModel):
    category_list: typing.List[ExportCategory]
