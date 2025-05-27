from pydantic import BaseModel


class SearchUserRequestType(BaseModel):
    keyword: str
